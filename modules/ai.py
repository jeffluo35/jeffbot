#!/usr/bin/env python3
# Artificial Intelligence (not really) module for Jeffbot

import jeffbot,logger
jeffbot.ai = 'ai'

words = {}

def process(input):
	template = "Input: "+' '.join(input)+" | Output: {0}"
	output = "<none>"
	if len(input) > 0:
		if input[0].lower() == 'learn' and 'as' in input:
			key = ' '.join(input[1:input.index('as')])
			value = ' '.join(input[input.index('as')+1:len(input)])
			words[key] = value
			output = 'Learned '+key+' as '+value
		elif input[0].lower() == 'unlearn' and len(input) > 1:
			del input[0]
			if ' '.join(input) in words:
				del words[' '.join(input)]
				output = 'Deleted '+' '.join(input)+' from the list of known words'
			else:
				output = 'Word not found'
		elif ' '.join(input) in words:
			output = words[' '.join(input)]
	return template.format(output)

logger.log(2,'Loaded ai module')
