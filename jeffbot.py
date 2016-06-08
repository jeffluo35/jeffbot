#!/usr/bin/env python3
# jeffl35's IRC bot

import socket,threading,re,queue,subprocess,hashlib,sys,io,os,code,importlib
from time import sleep
import logger,config

version = "Jeffbot v0.2-alpha https://github.com/jeffluo35/jeffbot"
class cmds:
	def login(msg,chan,host):
		if chan.startswith("#"):
			sendMsg(chan,host[0]+": "+"Not a good idea to show everybody your password.")
		try:
			if msg[1] in config.logins:
				if config.logins[msg[1]][0] == hashlib.sha512(msg[2].encode('utf-8')).hexdigest():
					sendMsg(chan,host[0]+": "+"Login succeeded")
					config.levels[host[2]] = config.logins[msg[1]][1]
				else:
					sendMsg(chan,host[0]+": "+"Username and/or password incorrect")
			else:
				sendMsg(chan,host[0]+": "+"Username and/or password incorrect")
		except IndexError:
			sendMsg(chan,"Not enough arguments. Usage: "+config.cmdchar+"login <username> <password>")
	def logout(msg,chan,host):
		try:
			del config.levels[host[2]]
			sendMsg(chan,host[0]+": Successfully logged out")
		except KeyError:
			sendMsg(chan,host[0]+": You are not logged in")
	def reload(msg,chan,host):
		importlib.reload(config)
		reloadevent.set()
		sendMsg(chan,'Reloading modules...')
	def version(msg,chan,host):
		sendMsg(chan,host[0]+": "+version)
	def source(msg,chan,host):
		sendMsg(chan,host[0]+": "+version)
	def dot(msg,chan,host):
		sendMsg(chan,"...................................")
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
	def sendto(msg,chan,host):
		if not checklvl(chan,host,9):
			return False
		if msg[1].lower().endswith("serv"):
			if not checklvl(chan,host,10):
				return False
		del msg[0]
		chan = msg[0]
		del msg[0]
		sendMsg(chan," ".join(msg))
	def nick(msg,chan,host):
		if not checklvl(chan,host,9):
			return False
		try:
			config.ircnick = msg[1]
			send("NICK "+msg[1]+"\n")
			logger.log(2,host[0]+" changed bot nick to "+msg[1])
		except IndexError:
			sendMsg(chan,"Not enough arguments. Usage: "+cmdchar+"nick <newnick>")
	def flushq(msg,chan,host):
		if not checklvl(chan,host,3):
			return False
		sendMsgQueue.queue.clear()
		sendMsg(chan,"Send queue cleared")
	def echoraw(msg,chan,host):
		if not checklvl(chan,host,10):
			return False
		del msg[0]
		send(" ".join(msg)+"\n")
	def setlvl(msg,chan,host):
		if not checklvl(chan,host,10):
			return False
		try:
			if int(msg[2]) == 0:
				del config.levels[msg[1]]
				sendMsg(chan,"Removed "+msg[1]+" from the permissions database")
			else:
				config.levels[msg[1]] = int(msg[2])
				sendMsg(chan,"Permission level of "+msg[1]+" set to "+msg[2])
		except IndexError:
			sendMsg(chan,"Not enough arguments. Usage: "+config.cmdchar+"setlvl [host] <level>")
		except ValueError:
			sendMsg(chan,"Incorrect syntax. Usage: "+config.cmdchar+"setlvl [host] <level>")
		except KeyError:
			sendMsg(chan,"User does not exist in permissions database.")
	def restart(msg,chan,host):
		if not checklvl(chan,host,10):
			return False
		os.execv("run.py",sys.argv)
	def dorelay(msg,chan,host):
		if not checklvl(chan,host,9):
			return False
		global dorelay
		dorelay = not dorelay
		sendMsg(chan,"dorelay set to "+str(dorelay))
	def listrelay(msg,chan,host):
		if not checklvl(chan,host,9):
			return False
		for relay in relays:
			sendMsg(chan,str(relays.index(relay))+": "+str(relay))
	def addrelay(msg,chan,host):
		if not checklvl(chan,host,9):
			return False
		if len(msg) < 3:
			sendMsg(chan,"Not enough arguments. Usage: "+config.cmdchar+"addrelay <chan1> <chan2> [chan3] [chan4]...")
		else:
			del msg[0]
			relays.append([channel.lower() for channel in msg])
			sendMsg(chan,"Done")
	def delrelay(msg,chan,host):
		if not checklvl(chan,host,9):
			return False
		try:
			del relays[int(msg[1])]
			sendMsg(chan,"Done")
		except IndexError:
			sendMsg(chan,"Not enough arguments. Usage: "+config.cmdchar+"delrelay <relay index>, where relay index is the index given by "+config.cmdchar+"listrelay")
		except ValueError:
			sendMsg(chan,"Syntax error. Usage: "+config.cmdchar+"delrelay <relay index>, where relay index is the index given by "+config.cmdchar+"listrelay")
	def addsilentchan(msg,chan,host):
		if not checklvl(chan,host,9):
			return False
		if len(msg) < 2:
			sendMsg(chan,"Not enough arguments. Usage: "+config.cmdchar+"addsilentchan <chan1> [chan2]...")
			return False
		del msg[0]
		relaymuted.append([channel.lower() for channel in msg])
		sendMsg(chan,"Done")
	def listsilentchan(msg,chan,host):
		if not checklvl(chan,host,9):
			return False
		i = 0
		for channel in relaymuted:
			sendMsg(chan,str(i)+": "+str(channel))
			i += 1
	def delsilentchan(msg,chan,host):
		if not checklvl(chan,host,9):
			return False
		try:
			del relaymuted[int(msg[1])]
			sendMsg(chan,"Done")
		except IndexError:
			sendMsg(chan,"Not enough arguments. Usage: "+config.cmdchar+"delsilentchan <channel index>, where channel index is the index given by "+config.cmdchar+"listsilentchan")
		except ValueError:
			sendMsg(chan,"Syntax error. Usage: "+config.cmdchar+"delsilentchan <channel index>, where channel index is the index given by "+config.cmdchar+"listsilentchan")
	def join(msg,chan,host):
		if not checklvl(chan,host,6):
			return False
		try:
			join(msg[1])
		except IndexError:
			sendMsg(chan,"Not enough arguments. Usage: "+config.cmdchar+"join <channel>")
	def part(msg,chan,host):
		if not checklvl(chan,host,6):
			return False
		try:
			part(msg[1])
		except IndexError:
			part(chan)
	def gtfo(msg,chan,host):
		if not checklvl(chan,host,6):
			return False
		sendMsg(chan,"\x01ACTION runs\x01")
		sleep(0.5)
		part(chan)
	def quit(msg,chan,host):
		if not checklvl(chan,host,10):
			return False
		del msg[0]
		if len(msg) > 0:
			send("QUIT :"+" ".join(msg)+"\n")
			logger.log(2,"Quitting. Requested by "+host[0]+" (hostname "+host[2]+") with reason "+" ".join(msg))
		else:
			send("QUIT :mooo\n")
			logger.log(2,"Quitting. Requested by "+host[0]+" (hostname "+host[2]+") with reason mooo")
		sleep(2)
		exit()
	def eval(msg,chan,host):
		if not checklvl(chan,host,10):
			return False
		if len(msg) > 1:
			try:
				del msg[0]
				sendMsg(chan,str(eval(" ".join(msg))))
			except Exception as e:
				sendMsg(chan,type(e).__name__+": "+str(e))
	def exec(msg,chan,host):
		if not checklvl(chan,host,10):
			return False
		if len(msg) > 1:
				del msg[0]
				result = subprocess.check_output(" ".join(msg)+"; return 0",shell=True,stderr=subprocess.STDOUT).decode('utf-8')
				result = result.split("\n")
				del result[-1]
				for line in result:
					sendMsg(chan,line)
	def py(msg,chan,host):
		if not checklvl(chan,host,10):
			return False
		global console
		if len(msg) > 1:
			if msg[1].lower() == "init":
				allvars = globals().copy()
				allvars.update(locals())
				console = code.InteractiveConsole(allvars)
				sendMsg(chan,"Console initialized")
			else:
				if console == None:
					cmds.py([msg[0],'init'],chan,host)
				del msg[0]
				sys.stdout = out = io.StringIO()
				sys.stderr = out
				console.push(" ".join(msg))
				sys.stdout,sys.stderr = sys.__stdout__,sys.__stderr__
				result = out.getvalue().split('\n')
				del result[-1]
				for line in result:
					sendMsg(chan,line)
		else:
			sendMsg(chan,"Not enough arguments. Usage: "+config.cmdchar+"py <python code>, use "+config.cmdchar+"py<space> for new line")
class ctcp:
	def version(nick,msg):
		sendNotice(nick,"\x01VERSION "+version+"\x01")
	def ping(nick,msg):
		sendNotice(nick,"\x01PING "+msg[1]+"\x01")

class runlogic (threading.Thread):
	def __init__(self,head,msg):
		threading.Thread.__init__(self)
		self.head = head
		self.msg = msg
	def run(self):
		if self.msg == [] or self.head == []:
			return
		chan = "none"
		if len(self.head) > 1 and self.head[1] == "PRIVMSG":
			chan = self.head[2]
			host = re.split("[\!\@]",self.head[0])
			if chan == config.ircnick: # for PMs
				chan = host[0]
			if len(self.msg) > 0 and self.msg[0].startswith(config.cmdchar):
				self.msg[0] = self.msg[0].lstrip(config.cmdchar).lower()
				try:
					getattr(cmds,self.msg[0])(self.msg,chan,host)
				except AttributeError:
					if config.commandnotfound:
						sendMsg(chan,host[0]+': The command '+self.msg[0]+' was not found.')
			elif len(self.msg) > 0 and self.msg[0].startswith("\x01"):
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
		if self.head[0] == "PING":
			send("PONG :"+self.msg[0]+"\n")
		try:
			if self.head[1] == "433" and self.head[2] == "*" and self.head[3] == config.ircnick:
				orignick = config.ircnick
				config.ircnick += "_"
				send("NICK "+config.ircnick+"\n")
				logger.log(2,"Nickname "+orignick+" taken, using "+config.ircnick+" instead.")
		except IndexError:
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

cmdhook(cmds.py,'>>')
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
	if config.proxyserver != None:
		proxyserver = config.proxyserver.split(":")
		ircsock.connect((proxyserver[0], int(proxyserver[1])))
		send("CONNECT "+ircserver+":6667\n\n")
		sleep(config.proxywait)
	else:
		ircsock.connect((config.ircserver, 6667))
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
console = None
