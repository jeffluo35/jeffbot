#!/usr/bin/env python3
# jeffl35's IRC bot

import socket
import threading
from time import sleep
import re

ircserver = "irc.freenode.net"
ircchannel = "##powder-bots"
nick = "Jeffbot"
user = "Jeff"

global ircsock
ircsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

def send(data):
	ircsock.send(bytes(data, 'UTF-8'))
	data = data.strip('\n')
	print(data)

def join(chan):
	send("JOIN "+ chan +"\n")

def pong():
	if (data.find("PING") != -1) and (data.find("PRIVMSG") == -1): 
		i = datasplit.index("PING ") + i
		send("PONG :"+ datasplit[i] +"\n")

def read(bytes):
	rawdata = ircsock.recv(bytes).decode('utf-8')
	print(rawdata)
	global data,datasplit
	data = rawdata.strip('\n\r')
	datasplit = re.split("[\:\n]", data)

# Initially join a channel
class initjoin (threading.Thread):
	def run(self):
		sleep(3)
		join(ircchannel)

def respond(chan, what, response):
	if (what in datasplit) and (data.find("PRIVMSG") != -1) and (data.find(chan) != -1):
		send("PRIVMSG "+ chan +" :"+ response +"\n")

def main():
	ircsock.connect((ircserver, 6667))
	print("Connected to server")
	send("USER "+ nick +" 0 * :"+ user +"\n")
	send("NICK "+ nick +"\n")
	initialjoin = initjoin()
	initialjoin.start()
	
	while 1:
		read(4096)
		if (data != None):
			pong()
			respond(ircchannel, "moo", "moooo")
		else:
			continue
main()
