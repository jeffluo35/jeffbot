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
helphook('op','Ops a person in the current channel, requires level 5. When no arguments are given, ops you. Usage: {}op [nick]')
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
helphook('deop','Deops a person in the current channel, requires level 5. When no arguments are given, deops you. Usage: {}deop [nick]')
def voice(msg,chan,host):
	if not checklvl(chan,host,5):
		return False
	try:
		mode(chan,"+v",msg[1])
	except IndexError:
		mode(chan,"+v",host[0])
cmdhook(voice)
helphook('voice','Voices a person in the current channel, requires level 5. When no arguments are given, voices you. Usage: {}voice [nick]')
def devoice(msg,chan,host):
	if not checklvl(chan,host,5):
		return False
	try:
		mode(chan,"+v",msg[1])
	except IndexError:
		mode(chan,"+v",host[0])
cmdhook(devoice)
helphook('devoice','Devoices a person in the current channel, requires level 5. When no arguments are given, devoices you. Usage: {}devoice [nick]')
def stab(msg,chan,host):
	if not checklvl(chan,host,5): return False
	try:
		userhost = gethost(msg[1])
		if not userhost == False:
			mode(chan,"+q",userhost)
		else:
			sendMsg(chan,'No such nick')
	except IndexError:
		sendMsg(chan,"Not enough arguments. See help")
cmdhook(stab)
helphook('stab','Quiets somebody in a channel, requires level 5. Usage: {}stab <nick>')
def unstab(msg,chan,host):
	if not checklvl(chan,host,5): return False
	try:
		userhost = gethost(msg[1])
		if not userhost == False:
			mode(chan,"-q",userhost)
		else:
			sendMsg(chan,'No such nick')
	except IndexError:
		sendMsg(chan,"Not enough arguments. See help")
cmdhook(unstab)
helphook('unstab','Unquiets somebody in a channel, requires level 5. Usage: {}unstab <nick>')
def ckick(msg,chan,host):
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
		sendMsg(chan,"Not enough arguments. See help.")
cmdhook(ckick,'kick')
helphook('kick','Kicks <nick> from the current channel with reason [reason]. If no reason is given, the sender\'s nick is used. Usage: {}kick <nick> [reason]')
def kickme(msg,chan,host):
	kick(chan,host[0],"You told me to")
cmdhook(kickme)
helphook('kickme','Kicks yourself. Takes no arguments.')
def banme(msg,chan,host):
	mode(chan,"+b","*!*@"+host[2])
cmdhook(banme)
helphook('banme','Bans yourself, but doesn\'t kick you. Does not unban you.')
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
		sendMsg(chan,"Not enough arguments. See help")
cmdhook(cmode,'mode')
helphook('mode','Sets channel modes on the current channel, requires level 5. Usage: {}mode <mode> [parameters]')
def ban(msg,chan,host):
	if not checklvl(chan,host,5):
		return False
	try:
		mode(chan,"+b","*!*@"+msg[1])
	except IndexError:
		sendMsg(chan,"Not enough arguments. See help")
cmdhook(ban)
helphook('ban','Bans <host>, requires level 5. Usage: {}ban <host>')
def unban(msg,chan,host):
	if not checklvl(chan,host,5):
		return False
	try:
		mode(chan,"-b","*!*@"+msg[1])
	except IndexError:
		sendMsg(chan,"Not enough arguments. Usage: "+config.cmdchar+"unban <host>")
cmdhook(unban)
helphook('unban','Unbans <host>, requires level 5. Usage: {}unban <host>')
def kban(msg,chan,host):
	if not checklvl(chan,host,5):
		return False
	try:
		nick = msg[1]
		userhost = gethost(msg[1])
		del msg[0:2]
		if not userhost == False:
			mode(chan,"+b",userhost)
			kick(chan,nick," ".join(msg))
		else:
			sendMsg(chan,'No such nick')
	except IndexError:
		sendMsg(chan,"Not enough arguments. See help")
cmdhook(kban)
helphook('kban','Kickbans a user, requires level 5. Usage: {}kban <nick> [reason]')
logger.log(2,'Loaded channel operator module')
