#!/usr/bin/env
# -*- coding: utf-8 -*-
"""
This example finds the most often used words in the doc
"""
import 

if __name__ == '__main__':
	import sys
	# Use the Psyco python accelerator if available
	# See:
	# 	http://psyco.sourceforge.net
	try:
		import psyco
		psyco.full() # accelerate this program
	except ImportError:
		pass
	printhelp=False
	if len(sys.argv)<2:
		printhelp=True
	else:
		for arg in sys.argv[1:]:
			if arg.startswith('-'):
				arg=[a.strip() for a in arg.split('=',1)]
				if arg in ['-h','--help']:
					printhelp=True
				else:
					print 'ERR: unknown argument "'+arg+'"'
			else:
				pd=ParsedDocument(arg)
				usage=pd.getWordUsage()
				print arg
				print "There are",pd.totalWordCount(),'total words in this doc,',pd.uniqueWordCount(),'unique'
				print "The top ten most frequent words in this doc:"
				for i in range(10):
					print '\t',usage[i][0],usage[i][1]
					if printhelp:
						print 'Usage:'
						print '  mostFrequent.py [options]'
						print 'Options:'
						print '   NONE'