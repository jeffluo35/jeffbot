#!/usr/bin/env python3
# Jeffbot configuration

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

proxyserver = None
# Uncomment to use proxy server
#proxyserver = "proxy.ccsd.net:80"
proxywait = 5 # Set this higher if proxy is slow

levels = {"unaffiliated/jeffl35": 10, "unaffiliated/iovoid": 9, "unaffiliated/bowserinator": 9}
