#!/usr/bin/env python3
# Main module, contains commands for built-in functions

from jeffbot import *
import config,logger
import hashlib,code,os,sys,subprocess,io

def login(msg,chan,host):
	if chan.startswith("#"):
		sendMsg(chan,host[0]+": "+"Not a good idea to show everybody your password.")
	try:
		if msg[1] in config.logins:
			if config.logins[msg[1]][0] == hashlib.sha512(msg[2].encode('utf-8')).hexdigest():
				sendMsg(chan,host[0]+": "+"Login succeeded")
				config.levels[host[2]] = config.logins[msg[1]][1]
			else:
				sendMsg(chan,host[0]+": "+"Username and/or password incorrect")
		else:
			sendMsg(chan,host[0]+": "+"Username and/or password incorrect")
	except IndexError:
		sendMsg(chan,"Not enough arguments. See help.")
cmdhook(login)
helphook('login','Logs you into the bot. WARNING: DO NOT USE THIS IN A CHANNEL. Usage: {}login <username> <password>')
def logout(msg,chan,host):
	try:
		del config.levels[host[2]]
		sendMsg(chan,host[0]+": Successfully logged out")
	except KeyError:
		sendMsg(chan,host[0]+": You are not logged in")
cmdhook(logout)
helphook('logout','Logs you out of the bot. Takes no arguments.')
def cversion(msg,chan,host):
	sendMsg(chan,host[0]+": "+version)
cmdhook(cversion,'version')
helphook('version','Shows the version of the bot. Takes no arguments.')
def source(msg,chan,host):
	sendMsg(chan,host[0]+": "+version)
cmdhook(source)
helphook('source','Gives a link to the source code. Takes no arguments.')
def dot(msg,chan,host):
	sendMsg(chan,"...................................")
cmdhook(dot)
helphook('dot','Prints lots of dots. Takes no arguments.')
def dotdotdot(msg,chan,host):
	sendMsg(chan,"……………………………………………………………………………………………")
cmdhook(dotdotdot)
helphook('dotdotdot','Prints more dots than {}dot. Takes no arguments.')
def sendto(msg,chan,host):
	if not checklvl(chan,host,9):
		return False
	if msg[1].lower().endswith("serv"):
		if not checklvl(chan,host,10):
			return False
	del msg[0]
	chan = msg[0]
	del msg[0]
	sendMsg(chan," ".join(msg))
cmdhook(sendto)
helphook('sendto','Sends a message to a specific channel, requires level 9 or higher. Note: When sending to *Serv, level 10 is required. Usage: {}sendto <channel> <message>')
def nick(msg,chan,host):
	if not checklvl(chan,host,9):
		return False
	try:
		config.ircnick = msg[1]
		send("NICK "+msg[1]+"\n")
		logger.log(2,host[0]+" changed bot nick to "+msg[1])
	except IndexError:
		sendMsg(chan,"Not enough arguments. See help.")
cmdhook(nick)
helphook('nick','Changes the bot\'s nick, requires level 9 or higher. Usage: {}nick <newnick>')
def flushq(msg,chan,host):
	if not checklvl(chan,host,3):
		return False
	sendMsgQueue.queue.clear()
	sendMsg(chan,"Send queue cleared")
cmdhook(flushq)
helphook('flushq','Flushes the send queue of the bot globally. Requires level 3 or higher. Takes no arguments.')
def echoraw(msg,chan,host):
	if not checklvl(chan,host,10):
		return False
	del msg[0]
	send(" ".join(msg)+"\n")
cmdhook(echoraw)
helphook('echoraw','Sends a raw command to the server. Requires level 10. Usage: {}echoraw <command>')
def setlvl(msg,chan,host):
	if not checklvl(chan,host,10):
		return False
	try:
		if int(msg[2]) == 0:
			del config.levels[msg[1]]
			sendMsg(chan,"Removed "+msg[1]+" from the permissions database")
		else:
			config.levels[msg[1]] = int(msg[2])
			sendMsg(chan,"Permission level of "+msg[1]+" set to "+msg[2])
	except IndexError:
		sendMsg(chan,"Not enough arguments. See help.")
	except ValueError:
		sendMsg(chan,"Incorrect syntax. See help.")
	except KeyError:
		sendMsg(chan,"User does not exist in permissions database.")
cmdhook(setlvl)
helphook('setlvl','Sets the permission level of a hostmask. If level is 0, removes the hostmask from the permissions database. Usage: {}setlvl <host> <level>')
def restart(msg,chan,host):
	if not checklvl(chan,host,10):
		return False
	os.execv("run.py",sys.argv)
cmdhook(restart)
helphook('restart','Restarts the bot, requires level 10. Takes no arguments.')
def cdorelay(msg,chan,host):
	if not checklvl(chan,host,9):
		return False
	global dorelay
	dorelay = not dorelay
	sendMsg(chan,"dorelay set to "+str(dorelay))
cmdhook(cdorelay,'dorelay')
helphook('dorelay','Toggles the relay status, requires level 9. Takes no arguments.')
def listrelay(msg,chan,host):
	if not checklvl(chan,host,9):
		return False
	for relay in relays:
		sendMsg(chan,str(relays.index(relay))+": "+str(relay))
cmdhook(listrelay)
helphook('listrelay','Lists all relays, requires level 9. Takes no arguments.')
def addrelay(msg,chan,host):
	if not checklvl(chan,host,9):
		return False
	if len(msg) < 3:
		sendMsg(chan,"Not enough arguments. See help.")
	else:
		del msg[0]
		relays.append([channel.lower() for channel in msg])
		sendMsg(chan,"Done")
cmdhook(addrelay)
helphook('addrelay','Adds a relay to the relay list. Usage: {}addrelay <chan1> <chan2> [chan3] [chan4]...')
def delrelay(msg,chan,host):
	if not checklvl(chan,host,9):
		return False
	try:
		del relays[int(msg[1])]
		sendMsg(chan,"Done")
	except IndexError:
		sendMsg(chan,"Not enough arguments. Usage: "+config.cmdchar+"delrelay <relay index>, where relay index is the index given by "+config.cmdchar+"listrelay")
	except ValueError:
		sendMsg(chan,"Syntax error. Usage: "+config.cmdchar+"delrelay <relay index>, where relay index is the index given by "+config.cmdchar+"listrelay")
cmdhook(delrelay)
helphook('delrelay','Deletes the relay given its id (id can be found using listrelay')
def addsilentchan(msg,chan,host):
	if not checklvl(chan,host,9):
		return False
	if len(msg) < 2:
		sendMsg(chan,"Not enough arguments. Usage: "+config.cmdchar+"addsilentchan <chan1> [chan2]...")
		return False
	del msg[0]
	relaymuted.append([channel.lower() for channel in msg])
	sendMsg(chan,"Done")
cmdhook(addsilentchan)
helphook('addsilentchan','Add a silent channel, where relay messages won\'t be sent to, requires level 9. Usage: {}addsilentchan <channel>')
def listsilentchan(msg,chan,host):
	if not checklvl(chan,host,9):
		return False
	i = 0
	for channel in relaymuted:
		sendMsg(chan,str(i)+": "+str(channel))
		i += 1
cmdhook(listsilentchan)
helphook('listsilentchan','Lists silent channels, requires level 9. Takes no arguments.')
def delsilentchan(msg,chan,host):
	if not checklvl(chan,host,9):
		return False
	try:
		del relaymuted[int(msg[1])]
		sendMsg(chan,"Done")
	except IndexError:
		sendMsg(chan,"Not enough arguments. Usage: "+config.cmdchar+"delsilentchan <channel index>, where channel index is the index given by "+config.cmdchar+"listsilentchan")
	except ValueError:
		sendMsg(chan,"Syntax error. Usage: "+config.cmdchar+"delsilentchan <channel index>, where channel index is the index given by "+config.cmdchar+"listsilentchan")
cmdhook(delsilentchan)
helphook('delsilentchan','Deletes a channel from the silent channel list, requires level 9. Usage: {}delsilentchan <channel>')
def cjoin(msg,chan,host):
	if not checklvl(chan,host,6):
		return False
	try:
		join(msg[1])
	except IndexError:
		sendMsg(chan,"Not enough arguments. Usage: "+config.cmdchar+"join <channel>")
cmdhook(cjoin,'join')
helphook('join','Joins a channel, requires level 6. Usage: {}join <channel>')
def cpart(msg,chan,host):
	if not checklvl(chan,host,6):
		return False
	try:
		part(msg[1])
	except IndexError:
		part(chan)
cmdhook(cpart,'part')
helphook('part','Parts a channel, requires level 6. Usage: {}part <channel>')
def cgethost(msg,chan,host):
	try:
		userhost = gethost(msg[1])
		if userhost == False:
			sendMsg(chan,host[0]+': Nick does not exist')
		else:
			sendMsg(chan,host[0]+': '+userhost)
	except IndexError:
		sendMsg(chan,'Not enough arguments. See help')
cmdhook(cgethost,'gethost')
helphook('gethost','Gets the host of a nick. Usage: {}gethost <nick>')
def ignore(msg,chan,host):
	if not checklvl(chan,host,10):
		return False
	try:
		userhost = gethost(msg[1])
		if userhost == False:
			sendMsg(chan,'Nick does not exist')
			return False
		if not userhost in config.ignorelist:
			config.ignorelist.append(userhost)
			sendMsg(chan,host[0]+': Added '+userhost+' to the ignore list')
		else:
			sendMsg(chan,host[0]+': '+userhost+' is already in the ignore list!')
	except IndexError:
		sendMsg(chan,'Not enough arguments. See help')
cmdhook(ignore)
helphook('ignore','Completely ignore a host, requires level 10. Usage: {}ignore <nick>')
def unignore(msg,chan,host):
	if not checklvl(chan,host,10):
		return False
	try:
		userhost = gethost(msg[1])
		if userhost == False:
			sendMsg(chan,'Nick does not exist')
			return False
		if userhost in config.ignorelist:
			del config.ignorelist[config.ignorelist.index(userhost)]
			sendMsg(chan,host[0]+': Unignored '+userhost)
		else:
			sendMsg(chan,host[0]+': User not in ignore list')
	except IndexError:
		sendMsg(chan,'Not enough arguments. See help')
cmdhook(unignore)
helphook('unignore','Unignore a host, requires level 10. Usage: {}unignore <nick>')
def gtfo(msg,chan,host):
	if not checklvl(chan,host,6):
		return False
	sendMsg(chan,"\x01ACTION runs\x01")
	sleep(0.5)
	part(chan)
cmdhook(gtfo)
helphook('gtfo','Tells the bot to get out of the current channel (noisily), requires level 6. Takes no arguments')
def cquit(msg,chan,host):
	if not checklvl(chan,host,10):
		return False
	del msg[0]
	if len(msg) > 0:
		send("QUIT :"+" ".join(msg)+"\n")
		logger.log(2,"Quitting. Requested by "+host[0]+" (hostname "+host[2]+") with reason "+" ".join(msg))
	else:
		send("QUIT :mooo\n")
		logger.log(2,"Quitting. Requested by "+host[0]+" (hostname "+host[2]+") with reason mooo")
	sleep(2)
	exit()
cmdhook(cquit,'quit')
helphook('quit','Quits the bot, requires level 10.')
def ceval(msg,chan,host):
	if not checklvl(chan,host,10):
		return False
	if len(msg) > 1:
		try:
			del msg[0]
			sendMsg(chan,str(eval(" ".join(msg))))
		except Exception as e:
			sendMsg(chan,type(e).__name__+": "+str(e))
cmdhook(ceval,'eval')
cmdhook(ceval,'>')
helphook('>','See help for eval')
helphook('eval','Evaluates a python expression, requires level 10. Usage: {}eval <expr>')
def cexec(msg,chan,host):
	if not checklvl(chan,host,10):
		return False
	if len(msg) > 1:
			del msg[0]
			result = subprocess.check_output(" ".join(msg)+"; return 0",shell=True,stderr=subprocess.STDOUT).decode('utf-8')
			result = result.split("\n")
			del result[-1]
			for line in result:
				sendMsg(chan,line)
cmdhook(cexec,'exec')
cmdhook(cexec,'$')
helphook('$','See help for exec')
helphook('exec','Executes a program on the host computer, requires level 10. Usage: {}exec <program> [arg1]...')
def py(msg,chan,host):
	if not checklvl(chan,host,10):
		return False
	global console
	if len(msg) > 1:
		if msg[1].lower() == "init":
			allvars = globals().copy()
			allvars.update(locals())
			console = code.InteractiveConsole(allvars)
			sendMsg(chan,"Console initialized")
		else:
			if console == None:
				cmds.py([msg[0],'init'],chan,host)
			del msg[0]
			sys.stdout = out = io.StringIO()
			sys.stderr = out
			console.push(" ".join(msg))
			sys.stdout,sys.stderr = sys.__stdout__,sys.__stderr__
			result = out.getvalue().split('\n')
			del result[-1]
			for line in result:
				sendMsg(chan,line)
	else:
		sendMsg(chan,"Not enough arguments. Usage: "+config.cmdchar+"py <python code>, use "+config.cmdchar+"py<space> for new line")
cmdhook(py,'>>')
cmdhook(py)
helphook('py','Runs python code in an interactive console. Usage: {}py <python code>')
helphook('>>','See help for py')
logger.log(2,'Loaded main module')
