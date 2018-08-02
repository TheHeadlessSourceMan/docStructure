#!/usr/bin/env
# -*- coding: utf-8 -*-
"""
This class finds things for you
"""

class Finder:
	
	def getAll(itemType,fileSeletionTree):
		"""
		Get all of a given type of item from a fileSeletionTree as a simple list
		"""
		useYield=True
		if useYield:
			# this does not work for some reason!
			for k,v in fileSeletionTree.children.items():
				for i in v:
					if k==itemType:
						yield(i)
					else:
						getAll(itemType,i)
		else:
			results=[]
			for k,v in fileSeletionTree.children.items():
				for i in v:
					if k==itemType:
						if type(i)==list:
							raise Exception
						results.append(i)
					else:
						for r in getAll(itemType,i):
							if type(r)==list:
								raise Exception
							results.append(r)
			#return results

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
				print 'ERR: unknown argument "'+arg+'"'
	if printhelp:
		print 'Usage:'
		print '  Finder.py [options]'
		print 'Options:'
		print '   NONE'