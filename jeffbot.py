#!/usr/bin/env python

# jeffl35's IRC bot

import socket
import thread
from time import sleep
import re

ircserver = "irc.freenode.net"
ircchannel = "##powder-bots"
nick = "Jeffbot"
user = "Jeff"

global data
global ircsock
ircsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Send data to the server, but also write it to stdout
def send(data):
	ircsock.send(data)
	data = data.strip('\n')
	print(data)

# Join a channel
def join(chan):
	send("JOIN "+ chan +"\n")

# Respond to pings
def pong():
	if (data.find("PING") != -1) and (data.find("PRIVMSG") == -1): 
		i = datasplit.index("PING ")
		i = i + 1
		send("PONG :"+ datasplit[i] +"\n")

# Recieve data from server
def read(bytes):
	rawdata = ircsock.recv(bytes)
	print(rawdata)
	data = rawdata.strip('\n\r')
	datasplit = re.split("[\:\n]", data)	

# Initially join a channel
def initjoin(chan):
	sleep(3)
	join(chan)

def respond(chan, what, response):
	if (what in datasplit) and (data.find("PRIVMSG") != -1) and (data.find(chan) != -1):
		print(data.find(what))
		send("PRIVMSG "+ chan +" :"+ response +"\n")

def main():
	ircsock.connect((ircserver, 6667))
	print("Connected to server")
	send("USER "+ nick +" 0 * :"+ user +"\n")
	send("NICK "+ nick +"\n")
	thread.start_new_thread(initjoin, (ircchannel,))
	
	while 1: # main loop
		read(4096)
		if (data != None):
			pong()
			respond(ircchannel, "moo", "moooo")
		else:
			continue
main()
