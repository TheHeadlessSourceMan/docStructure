#!/usr/bin/env
# -*- coding: utf-8 -*-
"""
This class represents a single character.  Most of the time
the smartest thing is to simply use a character, unless you have a situation where
a single character occupies multiple characters in the document, for instance, &gt;
"""
from DocFrag import *
import sys


class Character(DocFrag):
	"""
	This class represents a single character.  Most of the time
	the smartest thing is to simply use a character, unless you have a situation where
	a single character occupies multiple characters in the document, for instance, &gt;
	"""
	
	def __init__(self,doc,parent,position):
		"""
		:param doc: the document this paragraph belongs to
		:param parent: the parent object in the hierarchy
		:param position: the actual location of this item
		"""
		DocFrag.__init__(self,doc,parent,position)
		self.actual=None # actual character representation (a str or unicode)
		
	@property
	def words(self):
		"""
		get all words related to this frag
		"""
		return [self.parent]
		
	@property
	def sentences(self):
		"""
		get all sentences related to this frag
		(be it a parent sentence or child sentences)
		"""
		return [self.parent.parent]
		
	@property
	def paragraphs(self):
		"""
		get all sentences related to this frag
		(be it a parent paragraph or child paragraphs)
		"""
		return [self.parent.parent.parent]
		
	@property
	def chapters(self):
		"""
		get all chapters related to this frag
		(be it a parent paragraph or child chapters)
		"""
		return [self.parent.parent.parent.parent]
		
	def wordNum(self):
		"""
		word number within sentence
		"""
		return self.parent.wordNum()
		
	def sentenceNum(self):
		"""
		sentence number within paragraph
		"""
		return self.parent.parent.sentenceNum()
		
	def paragraphNum(self):
		"""
		para number within chapter
		"""
		return self.parent.parent.parent.paragraphNum()
		
	def chapterNum(self):
		"""
		chapter number within document
		"""
		return self.parent.parent.parent.parent.chapterNum()
		
	def __str__(self):
		return self.actual


if __name__ == '__main__':
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
		print '  Character.py [options]'
		print 'Options:'
		print '   NONE'