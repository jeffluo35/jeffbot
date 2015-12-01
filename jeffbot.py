#!/usr/bin/env python

# jeffl35's IRC bot

import socket
import thread
import time

ircserver = "irc.choopa.net"
ircchannel = "#nothing"
nick = "Jeffbot"
user = "Jeff"

# Join a channel
def join(chan):
	ircsock.send("JOIN "+ chan +"\n")

# Respond to pings
def pong():
	if (data.find("PING") != -1) and (data.find("PRIVMSG") == -1): 
		source = data.split(":")
		ircsock.send("PONG :"+ source[1] +"\n")
# Recieve data from server
def read(bytes):
	rawdata = ircsock.recv(bytes)
	print(rawdata)
	global data
	data = rawdata.strip('\n\r')

ircsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
ircsock.connect((ircserver, 6667))
ircsock.send("USER "+ nick +" 0 * :"+ user +"\n")
ircsock.send("NICK "+ nick +"\n")
time.sleep(3)
read(4096)
pong()
join(ircchannel)

while 1: # main loop
	read(4096)
	pong()
