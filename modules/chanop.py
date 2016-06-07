#!/usr/bin/env python3
# Channel operator commands for jeffbot

from jeffbot import *
import config
import logger

def op(msg,chan,host):
	if not checklvl(chan,host,5):
		return False
	try:
		mode(chan,"+o",msg[1])
	except IndexError:
		mode(chan,"+o",host[0])
cmdhook(op)
def deop(msg,chan,host):
	if not checklvl(chan,host,5):
		return False
	try:
		if msg[1] == config.ircnick:
			sendMsg(chan,"Why would I do that?")
			return False
		mode(chan,"-o",msg[1])
	except IndexError:
		mode(chan,"-o",host[0])
cmdhook(deop)
def voice(msg,chan,host):
	if not checklvl(chan,host,5):
		return False
	try:
		mode(chan,"+v",msg[1])
	except IndexError:
		mode(chan,"+v",host[0])
cmdhook(voice)
def devoice(msg,chan,host):
	if not checklvl(chan,host,5):
		return False
	try:
		mode(chan,"+v",msg[1])
	except IndexError:
		mode(chan,"+v",host[0])
cmdhook(devoice)
def kick(msg,chan,host):
	if not checklvl(chan,host,5):
		return False
	try:
		nick = msg[1]
		if nick.lower() == config.ircnick.lower():
			sendMsg(chan,"I don't see how kicking myself is possible")
			return False
		del msg[0:2]
		kick(chan,nick," ".join(msg))
	except IndexError:
		sendMsg(chan,"Not enough arguments. Usage: "+config.cmdchar+"kick <nick> [reason]")
cmdhook(kick)
def kickme(msg,chan,host):
	kick(chan,host[0],"You told me to")
cmdhook(kickme)
def banme(msg,chan,host):
	mode(chan,"+b","*!*@"+host[2])
cmdhook(banme)
def cmode(msg,chan,host):
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
		sendMsg(chan,"Not enough arguments. Usage: "+config.cmdchar+"mode <mode> [parameters]")
cmdhook(cmode,'mode')
def ban(msg,chan,host):
	if not checklvl(chan,host,5):
		return False
	try:
		mode(chan,"+b","*!*@"+msg[1])
	except IndexError:
		sendMsg(chan,"Not enough arguments. Usage: "+config.cmdchar+"ban <host>")
cmdhook(ban)
def unban(msg,chan,host):
	if not checklvl(chan,host,5):
		return False
	try:
		mode(chan,"-b","*!*@"+msg[1])
	except IndexError:
		sendMsg(chan,"Not enough arguments. Usage: "+config.cmdchar+"unban <host>")
cmdhook(unban)
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
		sendMsg(chan,"Not enough arguments. Usage: "+config.cmdchar+"kban <nick> <host> [reason]")
cmdhook(kban)
logger.log(2,'Loaded channel operator module')
