#!/usr/bin/env python3
# jeffl35's IRC bot

import socket
import threading
from time import sleep
import re
try:
	from ezzybot.util.repl import Repl
	enablesandbox = True
	sandboxinit = False
	sandbox = "uninitialized"
except ImportError:
	enablesandbox = False
ircserver = "164.132.77.237"
ircchannel = "##powder-bots"
# Make a file called "password" with your NickServ password in it
try:
	passfile = open("password", "r")
	password = passfile.read()
except FileNotFoundError:
	password = None
passfile.close()
nick = "Jeffbot"
user = "jeffbot"
name = "Jeff"
joinwait = 3
readbytes = 4096
cmdchar = "|"
version = "Jeffbot v0.2-alpha https://github.com/jeffluo35/jeffbot"

proxyserver = None
# Uncomment to use proxy server
#proxyserver = "proxy.ccsd.net:80"

levels = {"unaffiliated/jeffl35": 10, "unaffiliated/iovoid": 10, "unaffiliated/bowserinator": 10}
class commands:
	def dot(msg,chan,host):
		sendMsg(chan,"...................................")
	def echo(msg,chan,host):
		del msg[0]
		sendMsg(chan,"​"+" ".join(msg))
	def ping(msg,chan,host):
		sendMsg(chan, "pong")
	def pong(msg,chan,host):
		sendMsg(chan, "ping")
	def py(msg,chan,host):
		if not enablesandbox:
			sendMsg(chan,"Sandbox not enabled")
			return False
		if len(msg) > 1:
			if msg[1].lower() == "init":
				global sandbox
				global sandboxinit
				sandbox = Repl({"chan": chan, "msg": msg, "nick": nick})
				sendMsg(chan,"Done")
				sandboxinit = True
			elif not sandboxinit:
				sendMsg(chan,"Sandbox not initialized. Do "+cmdchar+"py init")
			else:
				global sandbox
				del msg[0]
				try:
					sendMsg(chan,sandbox.run(" ".join(msg)))
				except SystemExit:
					sendMsg(chan,"Definitely not doing that")
				except Exception as e:
					sendMsg(chan,str(type(e).__name__)+": "+str(e))
		else:
			sendMsg(chan,"Not enough arguments. Usage: "+cmdchar+"py <code> or "+cmdchar+"py init")
	def echoraw(msg,chan,host):
		if not checklvl(chan,host,10):
			return False
		del msg[0]
		send(" ".join(msg)+"\n")
	def join(msg,chan,host):
		if not checklvl(chan,host,5):
			return False
		try:
			join(msg[1])
		except IndexError:
			sendMsg(chan,"Not enough arguments. Usage: "+cmdchar+"join <channel>")
	def part(msg,chan,host):
		if not checklvl(chan,host,5):
			return False
		try:
			part(msg[1])
		except IndexError:
			part(chan)
	def eval(msg,chan,host):
		if not checklvl(chan,host,10):
			return False
		if len(msg) > 1:
			try:
				del msg[0]
				sendMsg(chan,str(eval(" ".join(msg))))
			except Exception as e:
				sendMsg(chan,type(e).__name__+": "+str(e))

class ctcp:
	def version(nick):
		sendNotice(nick,"\x01VERSION "+version+"\x01")

def runlogic(head,msg):
	if msg == [] or head == []:
		return
	chan = "none"
	if len(head) > 1 and head[1] == "PRIVMSG":
		chan = head[2]
		if len(msg) > 0 and msg[0].startswith(cmdchar):
			msg[0] = msg[0].strip(cmdchar).lower()
			host = re.split("[\!\@]",head[0])
			try:
				getattr(commands,msg[0])(msg,chan,host)
			except AttributeError:
				pass
		if len(msg) > 0 and msg[0].startswith("\x01"):
			msg[0] = msg[0].strip("\x01").lower()
			nick = head[0].split("!")[0]
			try:
				getattr(ctcp,msg[0])(nick)
			except AttributeError:
				pass
	pong(head,msg)

def send(data):
	ircsock.send(bytes(data, 'UTF-8'))
	data = data.strip('\n')
	print(data)

def sendMsg(chan,msg):
	if msg == "":
		send("PRIVMSG "+chan+" :None\n")
	else:
		send("PRIVMSG "+chan+" :"+msg+"\n")

def sendNotice(nick,msg):
	send("NOTICE "+nick+" :"+msg+"\n")

def join(chan):
	send("JOIN "+chan+"\n")

def part(chan):
	send("PART "+chan+"\n")

def checklvl(chan,host,lvl):
	try:
		if levels[host[2]] >= lvl:
			return True
		else:
			sendMsg(chan,host[0]+": You do not have enough permissions to use this command.")
			return False
	except KeyError:
		sendMsg(chan,host[0]+": You do not have enough permissions to use this command.")
		return False

def pong(head,msg):
	if head[0] == "PING":
		send("PONG :"+msg[0]+"\n")

def main():
	while 1:
		rawdata = ircsock.recv(readbytes).decode('utf-8')
		if rawdata != None:
			print(rawdata)
			data = rawdata.strip('\n\r').split("\n")
			for thing in data:
				datasplit = thing.split(":",2)
				i = 0
				for thing in datasplit:
					if i % 2 == 1:
						msg = thing.split()
					else:
						head = thing.split()
						if head == []:
							i -= 1
					i += 1
				try:
					runlogic(head,msg)
				except UnboundLocalError as e:
					print("Not an IRC message. Ignoring. Details: "+str(e))

# Initially join a channel
class initjoin (threading.Thread):
	def run(self):
		sleep(joinwait)
		join(ircchannel)

# set up the connection
def start():
	global proxyserver
	if proxyserver != None:
		proxyserver = proxyserver.split(":")
		ircsock.connect((proxyserver[0], int(proxyserver[1])))
		send("CONNECT "+ircserver+":6667\n\n")
		sleep(5)
	else:
		ircsock.connect((ircserver, 6667))
	print("Connected to server")
	if password != None:
		send("PASS "+password)
	send("USER "+user+" 0 * :"+name+"\n")
	send("NICK "+nick+"\n")
	initialjoin = initjoin()
	initialjoin.start()
	main()

ircsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
start()

