#!/usr/bin/env python3
# Launcher for jeffbot
# Also imports and reloads modules
import jeffbot,config
from importlib import reload
import glob
from os.path import dirname, basename, isfile

def findallmodules():
	modules = glob.glob(dirname(__file__)+"/modules/*.py")
	for f in modules:
		if isfile(f):
			module = basename(f)[:-3]
			if not module in config.modules:
				config.modules[basename(f)[:-3]] = None

config.modules = {}
findallmodules()
for module in config.modules:
	config.modules[module] = __import__('modules.'+module,globals(),locals(),[module])

jeffbot.start()
while config.running:
	jeffbot.reloadevent.wait()
	jeffbot.reloadevent.clear()
	findallmodules()
	for module in config.modules:
		if config.modules[module] is None:
			config.modules[module] = __import__('modules.'+module,globals(),locals(),[module])
		else:
			config.modules[module] = reload(config.modules[module])
