#!/usr/bin/env python3
# Stuff from tpt
# Blame jacob1 and cracker64 from irc.freenode.net/#powder

from jeffbot import *
import logger

def moo(msg,chan,host):
	sendMsg(chan,host[0]+": moooooooooOOOOOOOOOOOO!!!!!!!!!!")
cmdhook(moo)
helphook('moo','Mooooo!')
def potato(msg,chan,host):
	sendMsg(chan,"\x01ACTION is a potato\x01")
cmdhook(potato)
helphook('potato','Returns a rather untrue statement.')
logger.log(2,'Loaded tpt module')
