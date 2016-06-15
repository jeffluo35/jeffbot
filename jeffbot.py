#!/usr/bin/env python3
# jeffl35's IRC bot

import socket,threading,re,queue,sys,os,ssl
from time import sleep
import logger,config

version = "Jeffbot v0.2-alpha https://github.com/jeffluo35/jeffbot"
class cmds:
	def echo(msg,chan,host):
		del msg[0]
		sendMsg(chan,"​"+" ".join(msg))
	def secho(msg,chan,host):
		if not checklvl(chan,host,5):
			return False
		del msg[0]
		sendMsg(chan," ".join(msg))
	def ping(msg,chan,host):
		sendMsg(chan, "pong")
	def pong(msg,chan,host):
		sendMsg(chan, "ping")
	def reload(msg,chan,host):
		reloadevent.set()
		sendMsg(chan,'Reloading modules...')
	def help(msg,chan,host):
		try:
			sendMsg(chan,host[0]+": "+helpfile[msg[1]])
		except KeyError:
			sendMsg(chan,host[0]+": No help for that command")
		except IndexError:
			sendMsg(chan,host[0]+": Use "+config.cmdchar+"help <command> for help on a specific command, or "+config.cmdchar+"list to list commands")
	def list(msg,chan,host):
		commands = []
		for cmd in dir(cmds):
			if not cmd.startswith('__'):
				commands.append(cmd)
		sendMsg(chan,host[0]+": "+' '.join(commands))

class ctcp:
	def version(nick,msg):
		sendNotice(nick,"\x01VERSION "+version+"\x01")
	def ping(nick,msg):
		sendNotice(nick,"\x01PING "+msg[1]+"\x01")

class runlogic(threading.Thread):
	def __init__(self,head,msg):
		threading.Thread.__init__(self)
		self.head = head
		self.msg = msg
		self.ai = ai
	def run(self):
		if self.msg == [] or self.head == []:
			return
		chan = "none"
		if len(self.head) > 1:
			if self.head[1] == "PRIVMSG":
				chan = self.head[2]
				host = re.split("[\!\@]",self.head[0])
				if host[2] in config.ignorelist:
					return False
				if chan == config.ircnick: # for PMs
					chan = host[0]
				if len(self.msg) > 0:
					if self.msg[0].startswith(config.cmdchar):
						self.msg[0] = self.msg[0].lstrip(config.cmdchar).lower()
						try:
							if not self.msg[0].startswith('__'):
								getattr(cmds,self.msg[0])(self.msg,chan,host)
						except AttributeError:
							if config.commandnotfound:
								sendMsg(chan,host[0]+': The command '+self.msg[0]+' was not found.')
					elif ( not self.ai == None ) and self.msg[0].lower().startswith(config.ircnick.lower()):
						ai = __import__('modules.'+self.ai,globals(),locals(),[self.ai])
						del self.msg[0]
						sendMsg(chan,'['+host[0]+'] '+ai.process(self.msg))
					elif self.msg[0].startswith("\x01"):
						self.msg[0] = self.msg[0].lstrip("\x01").lower()
						self.msg[-1] = self.msg[-1].rstrip("\x01")
						try:
							getattr(ctcp,self.msg[0])(host[0],self.msg)
						except AttributeError:
							pass
					elif dorelay:
						for relay in relays:
							if chan.lower() in relay:
								if not chan.lower() in relaymuted:
									for channel in relay:
										if chan != channel:
											sendMsg(channel,"<"+host[0]+"@"+chan+"> "+" ".join(self.msg))
			elif self.head[1] == "311" and len(self.head) == 7:
				hostlist[self.head[3]] = self.head[5]
			elif self.head[1] == "401" and len(self.head) == 4:
				hostlist[self.head[3]] = False
		elif self.head[0] == "PING":
			send("PONG :"+self.msg[0]+"\n")

		try:
			if self.head[1] == "433" and self.head[2] == "*" and self.head[3] == config.ircnick:
				orignick = config.ircnick
				config.ircnick += "_"
				send("NICK "+config.ircnick+"\n")
				logger.log(2,"Nickname "+orignick+" taken, using "+config.ircnick+" instead.")
			elif self.head[1] == "KICK" and self.head[3] == config.ircnick and config.kickrejoin:
				join(self.head[2])
		except IndexError as e:
			pass

def send(data):
	with sendlock:
		ircsock.send(bytes(data, 'UTF-8'))
		data = data.rstrip('\r\n')
		logger.log(1,"[SEND] "+data)

def sendMsg(chan,msg):
	if msg == "":
		msg = " "
	maxlen = 449 - len(chan)
	msglen = sys.getsizeof(msg)
	if msglen > maxlen:
		for i in range(0, len(msg), maxlen):
			sendMsgQueue.put([chan,msg[i:i+maxlen]])
	else:
		sendMsgQueue.put([chan,msg])

class sendMessenger (threading.Thread):
	def __init__(self):
		threading.Thread.__init__(self)
	def run(self):
		while config.running:
			data = sendMsgQueue.get()
			send("PRIVMSG "+data[0]+" :"+data[1]+"\n")
			sleep(0.7)

def sendNotice(nick,msg):
	send("NOTICE "+nick+" :"+msg+"\n")

def join(chan):
	send("JOIN "+chan+"\n")

def part(chan):
	send("PART "+chan+"\n")

def kick(chan,nick,reason=config.ircnick):
	send("KICK "+chan+" "+nick+" :"+reason+"\n")

def mode(chan,mode,param=""):
	send("MODE "+chan+" "+mode+" "+param+"\n")

def gethost(nick):
	send("WHOIS "+nick+'\n')
	while config.running:
		for user in hostlist:
			if user.lower() == nick.lower():
				host = hostlist[user]
				del hostlist[user]
				return host
		else:
			sleep(0.25)

def checklvl(chan,host,lvl):
	msg = ": You do not have enough permissions to use this command."
	try:
		if config.levels[host[2]] >= lvl:
			return True
		else:
			sendMsg(chan,host[0]+msg)
			return False
	except KeyError:
		sendMsg(chan,host[0]+msg)
		return False

def cmdhook(name,cmdname=None):
	if cmdname == None:
		setattr(cmds,name.__name__,name)
	else:
		setattr(cmds,cmdname,name)

def helphook(name,desc):
	helpfile[name] = desc.format(config.cmdchar)

class main(threading.Thread):
	def __init__(self):
		threading.Thread.__init__(self)
	def run(self):
		while 1:
			rawdata = ircsock.recv(config.readbytes).decode('utf-8')
			if rawdata == "":
				break
			if rawdata != None:
				data = rawdata.rstrip('\r\n').split('\n')
				for thing in data:
					datasplit = thing.split(":",2)
					try:
						if datasplit[2].startswith(config.cmdchar+"login"):
							logger.log(1,"[RECV] :"+datasplit[1]+":[LOGIN INFORMATION]")
						else:
							logger.log(1,"[RECV] "+":".join(datasplit))
					except IndexError:
						logger.log(1,"[RECV] "+":".join(datasplit))
					i = 0
					for thing in datasplit:
						if i % 2 == 1:
							msg = thing.split(" ")
						else:
							head = thing.split()
							if head == []:
								i -= 1
						i += 1
					try:
						runlogic(head,msg).start()
					except UnboundLocalError as e:
						logger.log(3,"Not an IRC message, ignoring. Details: "+type(e).__name__+": "+str(e))
		logger.log(5,"Connection closed!")
		config.running = False
		sendMsgQueue.put(['',''])
		reloadevent.set()
		exit()

# Initially join channel(s)
class initjoin (threading.Thread):
	def run(self):
		sleep(config.joinwait)
		channels = config.ircchannels.split(",")
		for chan in channels:
			join(chan)

# set up the connection
def start():
	logger.log(2,version)
	if config.ssl:
		global ircsock
		ircsock = ssl.wrap_socket(sock=ircsock,do_handshake_on_connect=False)
	if config.proxyserver != None:
		proxyserver = config.proxyserver.split(":")
		ircsock.connect((proxyserver[0], int(proxyserver[1])))
		send("CONNECT "+config.ircserver+"\r\n\r\n")
		sleep(config.proxywait)
		if config.ssl:
			ircsock.do_handshake()
	else:
		ircserver = config.ircserver.split(":")
		ircsock.connect((ircserver[0], int(ircserver[1])))
		if config.ssl:
			ircsock.do_handshake()
	logger.log(2,"Connected to server")
	if config.password != None:
		send("PASS "+config.password+"\n")
	send("USER "+config.user+" 0 * :"+config.name+"\n")
	send("NICK "+config.ircnick+"\n")
	initjoin().start()
	sendMessenger().start()
	main().start()

ircsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sendlock = threading.Lock()
sendMsgQueue = queue.Queue()
dorelay = False
relays = []
relaymuted = []
reloadevent = threading.Event()
helpfile = {"echo": "Repeats the message with a zero-width space at the beginning, Usage: "+config.cmdchar+"echo <message>", "secho": "Repeats the message insecurely (requires level 5), Usage: "+config.cmdchar+"secho <message>", "ping": "Tells the bot to send a pong, has no arguments", "pong": "<AegisServer2> It's ping you moron.", "reload": "Reloads the bot's modules, has no arguments"}
hostlist = {}
console = None
ai = None
