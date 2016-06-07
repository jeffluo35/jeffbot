#!/usr/bin/env python3
# Launcher for jeffbot
# Also imports modules and reloads modules
import jeffbot,config
from modules import *
import importlib

jeffbot.start()

while config.running:
	jeffbot.reloadevent.wait()
	jeffbot.reloadevent.clear()
	for mod in __import__('modules').__all__:
		if not mod == "__init__":
			importlib.reload(globals()[mod])
