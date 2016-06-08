#!/usr/bin/env python3
# Module loader for jeffbot
# Finds all python files and puts them in __all__

from os.path import dirname, basename, isfile
import glob

modules = glob.glob(dirname(__file__)+"/*.py")
__all__ = []
for f in modules:
	if isfile(f) and not basename(f) is '__init__.py':
		__all__.append(basename(f)[:-3])
