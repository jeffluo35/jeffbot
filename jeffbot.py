#!/usr/bin/env python3
# jeffl35's IRC bot

import socket
import threading
from time import sleep

ircserver = "irc.freenode.net"
ircchannel = "##powder-bots"
nick = "Jeffbot"
user = "Jeff"
joinwait = 3
readbytes = 4096
cmdchar = "|"

# for testing purposes and because i'm lazy
def runlogic(head,msg):
	type = "raw"
	chan = "none"
	if len(head) > 1 and head[1] == "PRIVMSG":
		chan = head[2]
		if len(msg) > 0 and msg[0].startswith(cmdchar):
			msg[0] = msg[0].strip(cmdchar)
			type = "cmd"
			echo(msg,chan)
			joincmd(msg,chan)
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
	
def joincmd(msg,chan):
	try:
		if msg[0].lower() == "join":
			join(msg[1])
		elif msg[0].lower() == "part":
			part(msg[1])
	except IndexError:
		sendMsg(chan,"Not enough arguments. Usage: <"+cmdchar+"join|part> <channel>")
	
def pong(head,msg):
	if head[0] == "PING":
		send("PONG :"+msg[0]+"\n")
		
def echo(msg,chan):
	try:
		if msg[0].lower() == "echo":
			del msg[0]
			sendMsg(chan," ".join(msg))
	except IndexError:
		sendMsg(chan,"Not enough arguments. Usage: "+cmdchar+"echo <message>")

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
				runlogic(head,msg)

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
