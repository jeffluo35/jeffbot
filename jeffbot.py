#!/usr/bin/env python3
# jeffl35's IRC bot

import socket
import threading
from time import sleep
import re

ircserver = "164.132.77.237"
ircchannel = "##powder-bots"
nick = "Jeffbot"
user = "Jeff"
joinwait = 3
readbytes = 4096
cmdchar = "|"

global proxyserver
proxyserver = None
# Uncomment to use proxy server
#proxyserver = "proxy.ccsd.net:80"

powerusers = ["jeffl36!~jeffl35@unaffiliated/jeffl35", "jeffl35!~jeffl35@unaffiliated/jeffl35"]
class commands:
	def echo(msg,chan):
		del msg[0]
		sendMsg(chan,"​"+" ".join(msg))

class elevcommands:
	def checkIfElevated(head):
		if head[0] in powerusers:
			return True
		else:
			return False
	def echo(msg,chan):
		del msg[0]
		sendMsg(chan," ".join(msg))
	def join(msg,chan):
		try:
			join(msg[1])
		except IndexError:
			sendMsg(chan,"Not enough arguments. Usage: "+cmdchar+"join <channel>")
	def part(msg,chan):
		try:
			part(msg[1])
		except IndexError:
			part(chan)

def runlogic(head,msg):
	if msg == [] or head == []:
		return
	type = "raw"
	chan = "none"
	if len(head) > 1 and head[1] == "PRIVMSG":
		chan = head[2]
		if len(msg) > 0 and msg[0].startswith(cmdchar):
			msg[0] = msg[0].strip(cmdchar)
			type = "cmd"
			try:
				if elevcommands.checkIfElevated(head):
					try:
						getattr(elevcommands,msg[0])(msg,chan)
					except AttributeError:
						getattr(commands,msg[0])(msg,chan)	
				else:
					getattr(commands,msg[0])(msg,chan)
			except AttributeError:
				try:
					getattr(elevcommands,msg[0])
					sendMsg(chan,"You do not have the privileges to use this function!")
				except AttributeError:
					sendMsg(chan,"Command does not exist.")
	pong(head,msg)

def send(data):
	ircsock.send(bytes(data, 'UTF-8'))
	data = data.strip('\n')
	print(data)
	
def sendMsg(chan,msg):
	send("PRIVMSG "+chan+" :"+msg+"\n")

def join(chan):
	send("JOIN "+chan+"\n")

def part(chan):
	send("PART "+chan+"\n")
	
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
				except UnboundLocalError:
					print("Not an IRC message. Ignoring.")

# Initially join a channel
class initjoin (threading.Thread):
	def run(self):
		sleep(joinwait)
		join(ircchannel)

# set up the connection
def start():
	global ircsock
	ircsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	global proxyserver
	if proxyserver != None:
		proxyserver = proxyserver.split(":")
		ircsock.connect((proxyserver[0], int(proxyserver[1])))
		send("CONNECT "+ircserver+":6667\n\n")
		sleep(5)
	else:
		ircsock.connect((ircserver, 6667))
	print("Connected to server")
	send("USER "+ nick +" 0 * :"+ user +"\n")
	send("NICK "+ nick +"\n")
	initialjoin = initjoin()
	initialjoin.start()
	main()

start()

