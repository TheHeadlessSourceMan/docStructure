#!/usr/bin/env
# -*- coding: utf-8 -*-
"""
This program detects frequent words within all sentences
"""



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
				print argusage=pd.closestProximityOfWords()
				print "The top ten closest recurring words in this doc:"
				for i in range(10):
					sentence=pd.doc[usage[i][1].valueStart-20:usage[i][2].valueEnd+20]
					sentence=sentence.replace('\n',' ')
					print '\t',usage[i][0],'"'+usage[i][1].value()+'"','in',sentence
	if printhelp:
		print 'Usage:'
		print '  frequentSentence.py [options]'
		print 'Options:'
		print '   NONE'