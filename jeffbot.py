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
joinwait = 3
readbytes = 4096

# for testing purposes and because i'm lazy
def runcommands(head,msg):
	pong(head,msg)

def send(data):
	ircsock.send(bytes(data, 'UTF-8'))
	data = data.strip('\n')
	print(data)

def join(chan):
	send("JOIN "+ chan +"\n")

def pong(head,msg):
	if head[0] == "PING":
		send("PONG :"+msg[0]+"\n")

def main():
	while 1:
		rawdata = ircsock.recv(readbytes).decode('utf-8')
		if rawdata != None:
			print(rawdata)
			data = re.split("[\:\n]", rawdata.strip('\n\r'))
			i = 0
			for thing in data:
				if i > 1:
					runcommands(head,msg)
					i = 0
				if i % 2 == 1:
					msg = thing.split()
				else:
					head = thing.split()
					if head == []:
						i -= 1
				i += 1
			runcommands(head,msg)

# Initially join a channel
class initjoin (threading.Thread):
	def run(self):
		sleep(joinwait)
		join(ircchannel)

# set up the connection
def start():
	global ircsock
	ircsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	ircsock.connect((ircserver, 6667))
	print("Connected to server")
	send("USER "+ nick +" 0 * :"+ user +"\n")
	send("NICK "+ nick +"\n")
	initialjoin = initjoin()
	initialjoin.start()
	main()

start()
