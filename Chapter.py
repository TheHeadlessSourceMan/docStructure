#!/usr/bin/env
# -*- coding: utf-8 -*-
"""
This class represents a single chapter
"""
from DocFrag import *
from Paragraph import *
import re


class Chapter(DocFrag):
	"""
	This class represents a single chapter
	
	NOTE: chapter demarcations are defined by two or more consecutive newlines
	"""
	
	_SPLITTER=re.compile(r"""(?:\s*)(.+?)(?:(?:\s*\Z)|(?:\s*?\n(?:\s*\n)+))""",re.DOTALL)
	
	def __init__(self,doc,parent,position):
		"""
		:param doc: the document this paragraph belongs to
		:param parent: the parent object in the hierarchy
		:param position: the actual location of this item
		"""
		DocFrag.__init__(self,doc,parent,position)
		
	def set(self,location,text,title=None):
		"""
		Assign this paragraph to the given text.
		
		Will automatically update child items (sentences and words).
		
		:param location: set where this item is in the document
		:param text: set the text value
		"param title: the title of the chapter
		"""
		self.children=[]
		self.title=title
		for paragraphText in self._SPLITTER.finditer(text):
			position=(self.position[0]+paragraphText.start(1),self.position[0]+paragraphText.end(1))
			p=Paragraph(self.doc,self,position)
			p.set((paragraphText.start(1),paragraphText.end(1)),paragraphText.group(1))
			self.children.append(p)
			
	def chapterNum(self):
		"""
		chapter number within document
		"""
		return self.parent.chapters.index(self)
			
	@property
	def words(self):
		"""
		get all words related to this frag
		"""
		if self._words==None:
			self._words=[]
			for p in self.paragraphs:
				self._words.extend(p.words)
		return self._words
		
	@property
	def sentences(self):
		"""
		get all sentences related to this frag
		(be it a parent sentence or child sentences)
		"""
		if self._sentences==None:
			self._sentences=[]
			for p in self.paragraphs:
				self._sentences.extend(p.sentences)
		return self._sentences
		
	@property
	def paragraphs(self):
		"""
		get all sentences related to this frag
		(be it a parent paragraph or child paragraphs)
		"""
		return self.children
		
	@property
	def chapters(self):
		"""
		get all chapters related to this frag
		(be it a parent paragraph or child chapters)
		"""
		return [self]

		
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
		print '  Chapter.py [options]'
		print 'Options:'
		print '   NONE'