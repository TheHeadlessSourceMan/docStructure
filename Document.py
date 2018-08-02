#!/usr/bin/env
# -*- coding: utf-8 -*-
"""
This project breaks down any html-compatible document (which is everything, really) into sentences, words, parts of speech, etc
"""

#from nltk.parse.bllip import *
from DocFrag import *
from Chapter import *


NLTK_PARTS_OF_SPEECH={
	'CC':'Coordinating conjunction',
	'CD':'Cardinal number',
	'DT':'Determiner',
	'EX':'Existential there',
	'FW':'Foreign word',
	'IN':'Preposition or subordinating conjunction',
	'JJ':'Adjective',
	'JJR':'Adjective, comparative',
	'JJS':'Adjective, superlative',
	'LS':'List item marker',
	'MD':'Modal',
	'NN':'Noun, singular or mass',
	'NNS':'Noun, plural',
	'NNP':'Proper noun, singular',
	'NNPS':'Proper noun, plural',
	'PDT':'Predeterminer',
	'POS':'Possessive ending',
	'PRP':'Personal pronoun',
	'PRP$':'Possessive pronoun',
	'RB':'Adverb',
	'RBR':'Adverb, comparative',
	'RBS':'Adverb, superlative',
	'RP':'Particle',
	'SYM':'Symbol',
	'TO':'to',
	'UH':'Interjection',
	'VB':'Verb, base form',
	'VBD':'Verb, past tense',
	'VBG':'Verb, gerund or present participle',
	'VBN':'Verb, past participle',
	'VBP':'Verb, non-3rd person singular present',
	'VBZ':'Verb, 3rd person singular present',
	'WDT':'Wh-determiner',
	'WP':'Wh-pronoun',
	'WP$':'Possessive wh-pronoun',
	'WRB':'Wh-adverb'}
	

class FormatNotFoundException(Exception):
	def __init__(self,ext=None,mimeType=None):
		err='Format not found!'
		if ext!=None:
			err=err+' .'+ext
		if mimeType!=None:
			err=err+' '+mimeType
		Exception.__init__(self,err)
			

class DocumentBase(DocFrag):
	"""
	This class represents an entire doc
	"""
	
	_LEMMATIZER=None
	
	def __init__(self):
		DocFrag.__init__(self,self,None)
		self._linesLen=None
		self._wordInfo=None # {word:WordInfo}\

	def _wordRoot(self,text):
		"""
		get the undecorated version of a word:
			cat => cat
			cats => cat
			run => run
			ran => run
			running => run
		see:
			http://www.nltk.org/api/nltk.stem.html
		"""
		if self._LEMMATIZER==None:
			from nltk.stem import WordNetLemmatizer
			self._LEMMATIZER=WordNetLemmatizer()
		return self._LEMMATIZER.lemmatize(text)
		
	def set(self,text,name='[untitled]'):
		"""
		text - can be:
			a text buffer
			a filename
			a url (supports http:// https:// file:// ftp://)
		"""
		if text.find('\n')>=0:
			self.text=text
			self.location=None
		else:
			self.location=text
			location=text.split('://',1)
			if len(location)>1 and location[0]=='file':
				import urllib
				location=[urllib.url2pathname(location[1])]
			if len(location)>1:
				import urllib2
				f=urllib2.urlopen(self.location)
				text=f.read()
				f.close()
				text=unicode(text,errors='replace')
			else:
				f=open(location[0],'r')
				text=f.read()
				f.close()
				text=unicode(text,errors='replace')
		self.name=name
		self.text=text
		
	@property
	def children(self):
		if self._delegateDocument!=None:
			return self._delegateDocument.children
		ret=[]
		#for c in nltk.chap_tokenize(doc):
		#	c=Chapter(c)
		#	ret.append(c)
		c=Chapter(self,self)
		c.set(self.location,self.text)
		ret.append(c)
		return ret
		
	def offsToLine(self,location,zeroBased=False):
		"""
		converts a character location into (line,char_offset)
		
		if zeroBased=True, the first character is (0,0) otherwise it is (1,1)
		"""
		if self._delegateDocument!=None:
			return self._delegateDocument.offsToLine(location,zeroBased)
		if self._linesLen==None:
			self._linesLen=[]
			i=0
			for line in self.text.split('\n'):
				i=i+len(line)+1
				#print 'line end pos =',i
				self._linesLen.append(i)
		lineNo=0
		for lineLen in self._linesLen:
			if location<=lineLen:
				break
			lineNo+=1
		if lineNo==0:
			charNo=location
		else:
			charNo=location-self._linesLen[lineNo-1]
		if zeroBased:
			return (lineNo,charNo)
		return (1+lineNo,1+charNo)
			
	def uniqueWordCount(self):
		return len(self.getWordInfo().values())
		
	def getWordInfo(self):
		if self._wordInfo==None:
			self._wordInfo={}
			for word in getAll('word',self.fileSeletionTree):
				wordText=word.value()
				if not self._wordInfo.has_key(wordText):
					self._wordInfo[wordText]=WordInfo()
				self._wordInfo[wordText].locations.append(word)
		return self._wordInfo
		
	def getWordUsage(self):
		"""
		returns [(count,word)] for every word in the tree in order from greatest to least
		"""
		allwords=self.getWordInfo()
		results=[(len(w.locations),w) for w in allwords.values()]
		results.sort(key=lambda t: t[0],reverse=True)
		return results
	
	def closestProximityOfWords(self):
		"""
		gets the closes proximity of each word to itself
		returns (space_between,instance1,instance2)
		"""
		results=[]
		for w in self.getWordInfo().values():
			prox=w.closestProximity()
			if prox!=None:
				results.append(prox)
		results.sort(key=lambda t: t[0])
		return results
		
	@property
	def words(self):
		"""
		get all words related to this frag
		"""
		if self._words==None:
			self._words=[]
			for c in self.chapters:
				self._words.extend(c.words)
		return self._words
		
	@property
	def sentences(self):
		"""
		get all sentences related to this frag
		(be it a parent sentence or child sentences)
		"""
		#if self._doc!=None and self._delegateDocument:
		#	return self._doc.sentences
		if self._sentences==None:
			self._sentences=[]
			for c in self.chapters:
				self._sentences.extend(c.sentences)
		return self._sentences
		
	@property
	def paragraphs(self):
		"""
		get all sentences related to this frag
		(be it a parent paragraph or child paragraphs)
		"""
		#if self._doc!=None and self._delegateDocument:
		#	return self._doc.paragraphs
		if self._paragraphs==None:
			self._paragraphs=[]
			for c in self.chapters:
				self._paragraphs.extend(c.paragraphs)
		return self._paragraphs
		
	@property
	def chapters(self):
		"""
		get all chapters related to this frag
		(be it a parent paragraph or child chapters)
		"""
		#if self._doc!=None and self._delegateDocument:
		#	return self._doc.chapters
		return self.children
		
	@property
	def dataProvider(self):
		return self._dataProvider
		
		
class Document(object):#DocumentBase):
	def __init__(self,filename=None,data=None,mimeType=None):
		#DocumentBase.__init__(self)
		self._delegateDocument=None
		self.load(filename,data,mimeType)
		
	def __getattribute__(self,name):
		if name not in ['_delegateDocument','load']:
			return getattr(self._delegateDocument,name)
		return super(Document,self).__getattribute__(name)
		
	def load(self,filename,data=None,mimeType=None):
		"""
		filename - can be:
			* a file name
			* a URL #TODO:
			* a file-like object #TODO:
			* '-' to specify stdin
			* None if data is to be passed in instead
		
		data - if filename is None, pass in a data buffer
		
		mimeType - since we may not have a filename to go off, specify the file type
		"""
		ext=None
		if filename!=None:
			name=filename.rsplit('.',1)
			ext=name[-1].lower()
		else:
			if mimeType in ['text/plain',None]:
				ext='txt'
		if ext in ['txt','log','readme']:
			self._mimeType='text/plain'
			raise NotImplementedError('ERR: need a document type here')
		elif ext in ['htm','html','xhtml'] or mimeType=='text/html':
			import htmlDocument
			self._delegateDocument=htmlDocument.HtmlDocument(filename,data)
		else:
			try:
				import pyformatgenie
			except ImportError,e:
				print 'WARN: Should probably have pyformatgenie and some plugins installed!'
				raise FormatNotFoundException(ext,mimeType)
			pfg=pyformatgenie.PyFormatGenie()
			formats=pfg.findFormats(filename,mimeType,data)
			for fmt in formats:
				if True:#try:
					ob=fmt.load(filename)
				else:#except Exception,e:
					print 'ERR:'+str(e)+'\n\tWhen using type "'+fmt.name+'" to load "'+filename+'"'
					continue
				if isinstance(ob,DocumentBase):
					self._delegateDocument=ob
				elif hasattr(ob,'html') or 'html' in dir(ob):
					import htmlDocument
					self._delegateDocument=htmlDocument.HtmlDocument(ob)
				elif hasattr(ob,'text') or 'text' in dir(ob):
					raise NotImplementedError('ERR: need a document type here')
				else:
					print dir(ob)
					raise Exception(ob.__class__.__name__+' - No way to use this type of file!')
			if format==None:
				raise FormatNotFoundException(ext,mimeType)
			self._mimeType=mimeType

	
if __name__ == '__main__':
	import sys
	# Use the Psyco python accelerator if available
	# See:
	# 	http://psyco.sourceforge.net
	try:
		import psyco
		#psyco.full() # accelerate this program
	except ImportError:
		pass
	printhelp=False
	if len(sys.argv)<2:
		printhelp=True
	else:
		doc=None
		for arg in sys.argv[1:]:
			if arg.startswith('-'):
				arg=[a.strip() for a in arg.split('=',1)]
				arg[0]=arg[0].lower()
				if arg in ['-h','--help']:
					printhelp=True
				elif arg[0]=='--wordcount':
					print doc.wordCount
				elif arg[0]=='--sentencecount':
					print doc.sentenceCount
				elif arg[0]=='--paragraphcount':
					print doc.paragraphCount
				elif arg[0]=='--chaptercount':
					print doc.chapterCount
				elif arg[0]=='--words':
					print doc.words[int(arg[1])]
				elif arg[0]=='--sentences':
					print doc.sentences[int(arg[1])]
				elif arg[0]=='--paragraphs':
					print doc.paragraphs[int(arg[1])]
				elif arg[0]=='--chapters':
					print doc.chapters[int(arg[1])]
				elif arg[0]=='--html':
					if len(arg)>1:
						f=open(arg[1],'wb')
						f.write(doc.html)
						f.close()
					else:
						print doc.html
				elif arg[0]=='--text':
					if len(arg)>1:
						f=open(arg[1],'wb')
						f.write(doc.text)
						f.close()
					else:
						print doc.text
				else:
					print 'ERR: unknown argument "'+arg[0]+'"'
			else:
				print 'In',arg,':'
				doc=Document(arg)
	if printhelp:
		print 'Usage:'
		print '  Document.py file [commands]'
		print 'Commands:'
		print '  --wordCount ....... how many words'
		print '  --sentenceCount ... how many sentences'
		print '  --paragraphCount .. how many paragraphs'
		print '  --chapterCount .... how many chapters'
		print '  --word[n] ......... get words'
		print '  --sentence[n] ..... get sentences'
		print '  --paragraph[n] .... get paragraphs'
		print '  --chapter[n] ...... get chapters'
		print '  --text[=file] ..... convert to plain text (no file=stdout)'
		print '  --html[=file] ..... convert to html (no file=stdout)'