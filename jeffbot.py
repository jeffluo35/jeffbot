#!/usr/bin/env python

# jeffl35's IRC bot

import socket
import thread
import time

ircserver = "irc.freenode.net"
ircchannel = "##powder-bots"
nick = "Jeffbot"
user = "Jeff"

global ircsock
ircsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

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
		source = data.split(":")
		send("PONG :"+ source[1] +"\n")
		print("PONG :"+ source[1] +"\n")
# Recieve data from server
def read(bytes):
	rawdata = ircsock.recv(bytes)
	print(rawdata)
	global data
	data = rawdata.strip('\n\r')

ircsock.connect((ircserver, 6667))
print("Connected to server")
send("USER "+ nick +" 0 * :"+ user +"\n")
send("NICK "+ nick +"\n")
time.sleep(3)
read(4096)
pong()
join(ircchannel)

while 1: # main loop
	read(4096)
	pong()
