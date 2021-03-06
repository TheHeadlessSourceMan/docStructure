#!/usr/bin/env
# -*- coding: utf-8 -*-
"""
This class represents a single paragraph
"""
from DocFrag import *
from Sentence import *
from Location import *


class Paragraph(DocFrag):
	"""
	This class represents a single paragraph
	"""
	
	def __init__(self,doc,parent,position):
		"""
		:param doc: the document this paragraph belongs to
		:param parent: the parent object in the hierarchy
		:param position: the actual location of this item
		"""
		DocFrag.__init__(self,doc,parent,position)
		self._sentenceCount=None
		
	def set(self,location,text):
		"""
		Assign this paragraph to the given text.
		
		Will automatically update child items (sentences and words).
		
		:param location: set where this item is in the document
		:param text: set the text value
		"""
		self.location=location
		self.children=[]
		sentences=nltk.sent_tokenize(text)
		locations=findTokenLocations(text,sentences,self.location[0])
		for i in range(len(sentences)):
			sent=Sentence(self.doc,self,locations[i])
			sent.set(locations[i],sentences[i])
			self.children.append(sent)
			
	def paragraphNum(self):
		"""
		para number within chapter
		"""
		return self.parent.paragraphs.index(self)
		
	def chapterNum(self):
		"""
		chapter number within document
		"""
		return self.parent.chapterNum()
			
	@property
	def words(self):
		"""
		get all words related to this frag
		"""
		if self._words==None:
			self._words=[]
			for s in self.sentences:
				self._words.extend(s.words)
		return self._words
		
	@property
	def sentences(self):
		"""
		get all sentences related to this frag
		(be it a parent sentence or child sentences)
		"""
		return self.children
		
	@property
	def paragraphs(self):
		"""
		get all sentences related to this frag
		(be it a parent paragraph or child paragraphs)
		"""
		return [self]
		
	@property
	def chapters(self):
		"""
		get all chapters related to this frag
		(be it a parent paragraph or child chapters)
		"""
		return [self.parent]
	

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
		print '  Paragraph.py [options]'
		print 'Options:'
		print '   NONE'