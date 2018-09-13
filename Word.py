#!/usr/bin/env
# -*- coding: utf-8 -*-
"""
This class represents a single word
"""
from DocFrag import *
import sys


class WordInfo(object):
	"""
	Information about a word (such as definition, etc)
	"""
	
	def __init__(self):
		self.locations=[]
		self._definitions=None
		
	def wordName(self):
		return self.locations[0].value()
		
	def proximities(self):
		"""
		gets how near every instance of a word is to itsself
		
		:return: (space_between,instance1,instance2)
		"""
		for i in range(len(self.locations)-1):
			for j in range(i+1):
				if self.locations[i].valueStart != self.locations[j].valueStart:
					space_between=self.locations[i].valueEnd-self.locations[j].valueStart
					yield (space_between,self.locations[i],self.locations[j])
		
	def closestProximity(self):
		"""
		like proximities(), but only returns the closest two words
		
		:return: (space_between,instance1,instance2)
					can return None if there is one occurrence
		"""
		proximities=[x for x in self.proximities()]
		if len(proximities)==0:
			return None
		proximities.sort(key=lambda t: t[0])
		return proximities[0]
		#return sorted(self.proximities(),key=lambda t: t[0])[0]
		
	def getDefinitions(self):
		"""
		Get associated definition(s) for this word
		"""
		if self._definitions==None:
			import Dictionary
			self._definitions=Dictionary.getDefinitions(self.wordName)
		return self._definitions
		
	def __repr__(self):
		return self.wordName()

		
class Word(DocFrag):
	"""
	This class represents a single word
	"""
	
	_globalReferenceDictionary=None # there will be only one instance
	
	def __init__(self,doc,parent,position):#,value,doc=None,line=0,position=0):
		"""
		:param doc: the document this paragraph belongs to
		:param parent: the parent object in the hierarchy
		:param position: the actual location of this item
		"""
		DocFrag.__init__(self,doc,parent,position)
		#self.__eq__(value)
		self._syllables=None
		
	def set(self,location,text,partOfSpeech):
		"""
		:param location: set where this item is in the document
		:param text: set the text value
		:param partOfSpeech: what part of speech this word is
		"""
		self.location=location
		self.partOfSpeech=partOfSpeech
			
	def getRoot(self):
		"""
		Get the root/stem of this word.
		"""
		self.doc._wordRoot(self.__str__())
		
	@property
	def words(self):
		"""
		Get all words related to this frag
		"""
		return [self]
		
	@property
	def sentences(self):
		"""
		get all sentences related to this frag
		(be it a parent sentence or child sentences)
		"""
		return [self.parent]
		
	@property
	def paragraphs(self):
		"""
		get all sentences related to this frag
		(be it a parent paragraph or child paragraphs)
		"""
		return [self.parent.parent]
		
	@property
	def chapters(self):
		"""
		get all chapters related to this frag
		(be it a parent paragraph or child chapters)
		"""
		return [self.parent.parent.parent]
		
	def wordNum(self):
		"""
		word number within sentence
		"""
		return self.parent.words.index(self)
		
	def sentenceNum(self):
		"""
		sentence number within paragraph
		"""
		return self.parent.sentenceNum()
		
	def paragraphNum(self):
		"""
		para number within chapter
		"""
		return self.parent.parent.paragraphNum()
		
	def chapterNum(self):
		"""
		chapter number within document
		"""
		return self.parent.parent.parent.chapterNum()
		
	@property
	def referenceDictonary(self):
		"""
		:return: the reference dictionary -- will be automatically loaded as necessary
		"""
		if self.__class__._globalReferenceDictionary==None:
			print 'Loading dictionary...'
			import nltk
			from nltk.corpus import cmudict 
			self.__class__._globalReferenceDictionary=cmudict.dict()
		return self.__class__._globalReferenceDictionary
		
	@property
	def definition(self):
		"""
		:return: the (first) definition for this word
		"""
		return self.referenceDictonary[str(self).lower()]
		
	@property
	def syllables(self):
		"""
		:return: the number of syllables (useful when doing poetry)
		"""
		if self._syllables==None:
			text=unicode(self).lower().strip()
			if len(text)<1 or text[0].isalpha()==False:
				self._syllables=0
			else:
				try:
					self._syllables=[len(list(y for y in x if y[-1].isdigit())) for x in self.referenceDictonary[text]][0]
				except KeyError:
					print 'WARN: Unable to find definition for "'+text.encode(sys.stdout.encoding,errors='replace')+'"'
					print '      '+self.descriptiveLocation(False)
					self._syllables=0
		return self._syllables


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
		print '  Word.py [options]'
		print 'Options:'
		print '   NONE'