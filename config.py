#!/usr/bin/env python3
# Jeffbot configuration

ircserver = "164.132.77.237:6697"
ssl = True # Whether to use ssl
ircchannels = "##bowserinator,##jeffl35,##powder-bots" # Use comma-separated list for multiple channels
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
commandnotfound = False # Complain if a command is not found
kickrejoin = True # Rejoin a channel if kicked

proxyserver = None
# Uncomment to use proxy server
#proxyserver = "proxy.ccsd.net:80"
proxywait = 5 # Set this higher if proxy is slow
# Predefined users who do not need to log in
levels = {"unaffiliated/jeffl35": 10, "unaffiliated/iovoid": 9, "unaffiliated/bowserinator": 9}
logins = {"username": ["b109f3bbbc244eb82441917ed06d618b9008dd09b3befd1b5e07394c706a8bb980b1d7785e5976ec049b46df5f1326af5a2ea6d103fd07c95385ffab0cacbc86",1]} # Dictionary in the form of {"username": ["password-hash",level]}

try:
	from logins import * # Optionally store passwords in a file
except ImportError:
	pass

running = True
ignorelist = []
