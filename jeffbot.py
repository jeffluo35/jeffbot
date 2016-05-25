#!/usr/bin/env python3
# jeffl35's IRC bot

import socket
import threading
import re
from importlib import reload
from time import sleep,asctime
import random
import subprocess
import logger,excuses

try:
	from ezzybot.util.repl import Repl
	enablesandbox = True
	sandboxinit = False
	sandbox = "uninitialized"
except ImportError:
	enablesandbox = False
# Sadly, sandboxes are humongous security issues
enablesandbox = False
ircserver = "164.132.77.237"
ircchannels = "##powder-bots,##bowserinator,##jeffl35" # Use comma-separated list for multiple channels
# Make a file called "password" with your NickServ password in it
try:
	passfile = open("password", "r")
	password = passfile.read()
	passfile.close()
except FileNotFoundError:
	password = None
ircnick = "Jeffbot"
user = "jeffbot"
name = "Jeff"
joinwait = 2
readbytes = 4096
cmdchar = "|"
version = "Jeffbot v0.2-alpha https://github.com/jeffluo35/jeffbot"

proxyserver = None
# Uncomment to use proxy server
#proxyserver = "proxy.ccsd.net:80"

levels = {"unaffiliated/jeffl35": 10, "unaffiliated/iovoid": 9, "unaffiliated/bowserinator": 9}
class commands:
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
	def excuse(msg,chan,host):
		sendMsg(chan, random.choice(excuses.excuses))
	def moo(msg,chan,host):
		sendMsg(chan,host[0]+": moooooooooOOOOOOOOOOOO!!!!!!!!!!")
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
					output = sandbox.run(" ".join(msg)).split("\n")
					del output[0]
					for line in output:
						sendMsg(chan,host[0]+": "+line)
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
	def setlvl(msg,chan,host):
		if not checklvl(chan,host,10):
			return False
		global levels
		try:
			if int(msg[2]) == 0:
				del levels[msg[1]]
				sendMsg(chan,"Removed "+msg[1]+" from the permissions database")
			else:
				levels[msg[1]] = int(msg[2])
				sendMsg(chan,"Permission level of "+msg[1]+" set to "+msg[2])
		except IndexError:
			sendMsg(chan,"Not enough arguments. Usage: "+cmdchar+"setlvl [host] <level>")
		except ValueError:
			sendMsg(chan,"Incorrect syntax. Usage: "+cmdchar+"setlvl [host] <level>")
		except KeyError:
			sendMsg(chan,"User does not exist in permissions database.")
	def restart(msg,chan,host):
		if not checklvl(chan,host,10):
			return False
		__import__("os").execv(__file__,__import__("sys").argv)
	def op(msg,chan,host):
		if not checklvl(chan,host,5):
			return False
		try:
			mode(chan,"+o",msg[1])
		except IndexError:
			mode(chan,"+o",host[0])
	def deop(msg,chan,host):
		if not checklvl(chan,host,5):
			return False
		try:
			if msg[1] == ircnick:
				sendMsg(chan,"Why would I do that?")
				return False
			mode(chan,"-o",msg[1])
		except IndexError:
			mode(chan,"-o",host[0])
	def voice(msg,chan,host):
		if not checklvl(chan,host,5):
			return False
		try:
			mode(chan,"+v",msg[1])
		except IndexError:
			mode(chan,"+v",host[0])
	def devoice(msg,chan,host):
		if not checklvl(chan,host,5):
			return False
		try:
			mode(chan,"+v",msg[1])
		except:
			mode(chan,"+v",host[0])
	def kick(msg,chan,host):
		if not checklvl(chan,host,5):
			return False
		try:
			nick = msg[1]
			if nick.lower() == ircnick.lower():
				sendMsg(chan,"I don't see how kicking myself is possible")
				return False
			del msg[0:2]
			kick(chan,nick," ".join(msg))
		except IndexError: 
			sendMsg(chan,"Not enough arguments. Usage: "+cmdchar+"kick <nick> [reason]")
	def kickme(msg,chan,host):
		kick(chan,host[0],"You told me to")
	def banme(msg,chan,host):
		mode(chan,"+b","*!*@"+host[2])
	def mode(msg,chan,host):
		if not checklvl(chan,host,5):
			return False
		try:
			cmode = msg[1]
			del msg[0:2]
			if len(msg) > 0:
				mode(chan,cmode," ".join(msg))
			else:
				mode(chan,cmode)
		except IndexError:
			sendMsg(chan,"Not enough arguments. Usage: "+cmdchar+"mode <mode> [parameters]")
	def ban(msg,chan,host):
		if not checklvl(chan,host,5):
			return False
		try:
			mode(chan,"+b","*!*@"+msg[1])
		except IndexError:
			sendMsg(chan,"Not enough arguments. Usage: "+cmdchar+"ban <host>")
	def unban(msg,chan,host):
		if not checklvl(chan,host,5):
			return False
		try:
			mode(chan,"-b","*!*@"+msg[1])
		except IndexError:
			sendMsg(chan,"Not enough arguments. Usage: "+cmdchar+"unban <host>")
	def kban(msg,chan,host):
		if not checklvl(chan,host,5):
			return False
		try:
			nick = msg[1]
			host = msg[2]
			del msg[0:3]
			mode(chan,"+b",host)
			kick(chan,nick," ".join(msg))
		except IndexError:
			sendMsg(chan,"Not enough arguments. Usage: "+cmdchar+"kban <nick> <host> [reason]")
			
	def join(msg,chan,host):
		if not checklvl(chan,host,6):
			return False
		try:
			join(msg[1])
		except IndexError:
			sendMsg(chan,"Not enough arguments. Usage: "+cmdchar+"join <channel>")
	def part(msg,chan,host):
		if not checklvl(chan,host,6):
			return False
		try:
			part(msg[1])
		except IndexError:
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
class ctcp:
	def version(nick):
		sendNotice(nick,"\x01VERSION "+version+"\x01")

def runlogic(head,msg):
	if msg == [] or head == []:
		return
	chan = "none"
	if len(head) > 1 and head[1] == "PRIVMSG":
		chan = head[2]
		host = re.split("[\!\@]",head[0])
		if chan == ircnick: # for PMs
			chan = host[0]
		if len(msg) > 0 and msg[0].startswith(cmdchar):
			msg[0] = msg[0].strip(cmdchar).lower()
			try:
				getattr(commands,msg[0])(msg,chan,host)
			except AttributeError:
				pass
		if len(msg) > 0 and msg[0].startswith("\x01"):
			msg[0] = msg[0].strip("\x01").lower()
			try:
				getattr(ctcp,msg[0])(host[0])
			except AttributeError:
				pass
	if head[0] == "PING":
		send("PONG :"+msg[0]+"\n")

def send(data):
	ircsock.send(bytes(data, 'UTF-8'))
	data = data.strip('\r\n')
	logger.log(1,"[SEND] "+data)

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
	msg = ": You do not have enough permissions to use this command."
	try:
		if levels[host[2]] >= lvl:
			return True
		else:
			sendMsg(chan,host[0]+msg)
			return False
	except KeyError:
		sendMsg(chan,host[0]+msg)
		return False

def kick(chan,nick,reason=ircnick):
	send("KICK "+chan+" "+nick+" :"+reason+"\n")

def mode(chan,mode,param=""):
	send("MODE "+chan+" "+mode+" "+param+"\n")

def who(nick):
	global catch
	send("WHO "+nick)

def main():
	while 1:
		rawdata = ircsock.recv(readbytes).decode('utf-8')
		if rawdata == "":
			break
		if rawdata != None:
			data = rawdata.strip('\r\n').split('\n')
			for thing in data:
				logger.log(1,"[RECV] "+thing)
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
					logger.log(3,"Not an IRC message, ignoring. Details: "+type(e).__name__+": "+str(e))
	logger.log(5,"Connection closed!")
	exit()

# Initially join channel(s)
class initjoin (threading.Thread):
	def run(self):
		sleep(joinwait)
		channels = ircchannels.split(",")
		for chan in channels:
			join(chan)

# set up the connection
def start():
	logger.log(2,version)
	global proxyserver
	if proxyserver != None:
		proxyserver = proxyserver.split(":")
		ircsock.connect((proxyserver[0], int(proxyserver[1])))
		send("CONNECT "+ircserver+":6667\n\n")
		sleep(5)
	else:
		ircsock.connect((ircserver, 6667))
	logger.log(2,"Connected to server")
	if password != None:
		send("PASS "+password+"\n")
	send("USER "+user+" 0 * :"+name+"\n")
	send("NICK "+ircnick+"\n")
	initialjoin = initjoin()
	initialjoin.start()
	main()

ircsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

start()
