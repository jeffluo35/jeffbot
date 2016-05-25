#!/usr/bin/env python3
# Logging module for jeffbot

from time import asctime

def log(lvl,msg):
	if lvl == 0:
		l = "DEBUG"
	elif lvl == 1:
		l = "INFO"
	elif lvl == 2:
		l = "NOTICE"
	elif lvl == 3:
		l = "WARNING"
	elif lvl == 4:
		l = "ERROR"
	elif lvl == 5:
		l = "CRITICAL"
	print(asctime()+" ["+l+"] "+msg)
