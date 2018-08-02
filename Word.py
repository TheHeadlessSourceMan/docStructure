#!/usr/bin/env
# -*- coding: utf-8 -*-
"""
This class represents a single word
"""
from DocFrag import *
import sys

class WordInfo(object):
	def __init__(self):
		self.locations=[]
		self._definitions=None
		
	def wordName(self):
		return self.locations[0].value()
		
	def proximities(self):
		"""
		gets how near every instance of a word is to itsself
		returns (space_between,instance1,instance2)
		"""
		for i in range(len(self.locations)-1):
			for j in range(i+1):
				if self.locations[i].valueStart != self.locations[j].valueStart:
					space_between=self.locations[i].valueEnd-self.locations[j].valueStart
					yield (space_between,self.locations[i],self.locations[j])
		
	def closestProximity(self):
		"""
		like proximities(), but only returns the closest two words
		returns (space_between,instance1,instance2)
		(can return None if there is one occourance)
		"""
		proximities=[x for x in self.proximities()]
		if len(proximities)==0:
			return None
		proximities.sort(key=lambda t: t[0])
		return proximities[0]
		#return sorted(self.proximities(),key=lambda t: t[0])[0]
		
	def getDefinitions(self):
		if self._definitions==None:
			import Dictionary
			self._definitions=Dictionary.getDefinitions(self.wordName)
		return self._definitions
		
	def __str__(self):
		return self.wordName()

		
class Word(DocFrag):
	_globalReferenceDictionary=None # there will be only one instance
	
	def __init__(self,doc,parent):#,value,doc=None,line=0,position=0):
		DocFrag.__init__(self,doc,parent)
		#self.__eq__(value)
		self._syllables=None
		
	def set(self,location,text,partOfSpeech):
		self.location=location
		self.partOfSpeech=partOfSpeech
			
	def getRoot(self):
		self.doc._wordRoot(self.__str__())
		
	@property
	def words(self):
		"""
		get all words related to this frag
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
		if self.__class__._globalReferenceDictionary==None:
			print 'Loading dictionary...'
			import nltk
			from nltk.corpus import cmudict 
			self.__class__._globalReferenceDictionary=cmudict.dict()
		return self.__class__._globalReferenceDictionary
		
	@property
	def definition(self):
		return self.referenceDictonary[str(self).lower()]
		
	@property
	def syllables(self):
		"""
		get the number of syllables
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