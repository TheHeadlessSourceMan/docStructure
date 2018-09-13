#!/usr/bin/env
# -*- coding: utf-8 -*-
"""
Tools for finding and tracking doc location of text
"""
import nltk


def findTokenLocations(text,words,plusOffs=0):
	"""
	:param text: the original text
	:param words: words tokenized from the text (if None, will do it ourselves)
	:param plusOffs: add this to every value
	
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


class Location(object):
	"""
	Represents a location within a document
	"""
	
	def __init__(self,doc,position):
		"""
		:param doc: the document
		:param position: the actual location of this item
		"""
		self.doc=doc
		if position==None:
			raise Exception("Location with no position")
		self.position=position
	
	def getLocationString(self):
		"""
		return the location as a user-readable string
		"""
		return str(self.doc.name)+'@'+str(self.position)
	
	def __repr__(self):
		"""
		NOTE: This will probably be hidden by derived classes
		"""
		return self.getLocationString()
		
	@property
	def line(self):
		"""
		the (line,char_offset) of the start of this element
		
		NOTE: in wrapped text and marked-up documents this is not necessirily
		the line the reader is seeing, but is instead the line in the source doc
		descriptiveLocation() might be more what you're looking for
		"""
		return self.doc.offsToLine(self.location[0])
		
	# ---- implement comparison operators so we can locate things
	def __eq__(self,other):
		if isinstance(other,Location):
			return other.position[0]==self.position[0] and other.position[1]==self.position[1]
		return other>=self.position[0] and other<=self.position[1]
	def __ne__(self,other):
		return not self==other
	def __lt__(self,other):
		if isinstance(other,Location):
			other=other.position[0]
		return other<self.position[1]
	def __gt__(self,other):
		if isinstance(other,Location):
			other=other.position[1]
		return other>self.position[0]
	def __le__(self,other):
		if isinstance(other,Location):
			other=other.position[0]
		return other<=self.position[0]
	def __ge__(self,other):
		if isinstance(other,Location):
			other=other.position[1]
		return other>=self.position[1]
	

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