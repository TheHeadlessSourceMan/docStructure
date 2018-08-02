#!/usr/bin/env
# -*- coding: utf-8 -*-
"""
Tools for finding and tracking doc location of text
"""
import nltk

def findTokenLocations(text,words,plusOffs=0):
	"""
	text - the original text
	words - words tokenized from the text (if None, will do it ourselves)
	plusOffs - add this to every value
	
	returns [(start,end)] for all words
	"""
	if words==None:
		words=nltk.wordpunct_tokenize(text)
	e=0
	ret=[]
	for w in words:
		s=text.find(w,e)
		e=s+len(w)
		ret.append((s+plusOffs,e+plusOffs))
	return ret

class Location:
	def __init__(self,doc,line,position=0):
		self.doc=doc
		self.line=line
		self.position=position
	
	def getLocationString(self):
		return str(self.doc),self.line,self.position
	
	def __str__(self):
		"""
		NOTE: This will probably be hidden by derived classes
		"""
		return self.getLocationString()
	

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
		print '  Location.py [options]'
		print 'Options:'
		print '   NONE'