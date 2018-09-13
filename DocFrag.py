#!/usr/bin/env
# -*- coding: utf-8 -*-
"""
This is the base class for all Document components (Word,Paragraph,etc)
"""
from Location import Location
from pynode import *
import bisect # binary searching to speed things up


def txt2html(txt):
	"""
	convert plain text to html
	
	:param txt: plain text to convert
	:return: html
	
	NOTE: presently we directly munge the text
	NOTE: does not handle special chars like &u1234;
	"""
	replacements=[
		('&','&amp;')
		('  ',' &nbsp;'),
		('>','&gt;'),
		('<','&lt;'),
		('\r\n','\n'),
		('\n','<br />\n'),
		]
	for this,that in replacements:
		txt=txt.replace(this,that)
	return '<html>\n<head>\n\t<title></title>\n</head>\n<body>\n'+txt.strip()+'\n</body>\n</html>'

def html2txt(html):
	"""
	convert html to plain text
	
	:param html: html to convert
	:return: plain text
	
	Capable of using (in order):
		BeautifulSoup
		nltk (old)
		brute force text matching (not perfect)
			does not handle special chars like &u1234;
			ignores <pre>
	"""
	try:
		from bs4 import BeautifulSoup
		soup = BeautifulSoup(html)
		# kill all script and style elements
		for script in soup(["script", "style"]):
			script.extract()    # rip it out
		# get text
		text = soup.get_text()
		# break into lines and remove leading and trailing space on each
		lines = (line.strip() for line in text.splitlines())
		# break multi-headlines into a line each
		chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
		# drop blank lines
		return '\n'.join(chunk for chunk in chunks if chunk)
	except ImportError:
		pass
	try:
		import nltk
		return nltk.clean_html(html) 
	except Exception:
		pass
	replacements=[
		('  ',' '),
		('  ',' '),
		('&nbsp;',' '),
		('&gt;','>'),
		('&lt;','<'),
		('&amp;',' ')
		]
	ret=[]
	first=True
	ready=False
	html=html.replace('\n','').replace('\r','').replace('<br>','\n').replace('<br />','\n').replace('<br/>','\n')
	for h in html.split('<'):
		#print h
		if first:
			if ready:
				ret.append(h[0])
			first=False
		elif ready:
			ret.append(h.rsplit('>',1)[-1])
		elif len(h)>1 and h[1].startswith('body'):
			ready=True
	ret=' '.join(ret)
	for this,that in replacements:
		ret=ret.replace(this,that)
	return ret


class DocFrag(Node,Location):#(str):
	"""
	This is the base class for all Document components (Word,Paragraph,etc)
	"""
	
	def __init__(self,doc,parent,position):
		"""
		:param doc: the document this paragraph belongs to
		:param parent: the parent object in the hierarchy
		:param position: the actual location of this item
		"""
		#str.__init__(self)
		Node.__init__(self,self.__class__.__name__,parent=parent)
		Location.__init__(self,doc,position)
		#self.doc=doc
		self.parent=parent
		self._dataProvider=None # actual data this comes from
		#self.location=None # start and end character location within self.dataProvider
		self._words=None # a cache
		self._sentences=None # a cache
		self._paragraphs=None # a cache
		self.include=True # use this to skip a doc frag when compiling document
		
	@property
	def location(self):
		"""
		TODO: the terminology is confusing and should go away
		"""
		return self.position
	@location.setter
	def location(self,location):
		if location==None:
			raise Exception('Attempt to assign None to location')
		self.position=location
		
	@property
	def dataProvider(self):
		if self._dataProvider!=None:
			ret=self._dataProvider
		else:
			ret=self.parent.dataProvider
			if ret==None:
				ret=self.doc
		if ret==None:
			raise Exception(self.__class__.__name__+' - dataProvider has gone missing!!!')
		return ret
		
	@property
	def text(self):
		text=''
		dataProvider=self.dataProvider
		if dataProvider!=None:
			text=dataProvider.text
			if type(text)==None:
				text=''
			elif type(text)!=unicode:
				text=unicode(text,errors='replace')
		if self.location!=None:
			text=text[self.location[0]:self.location[1]]
		return text
	@text.setter
	def text(self,value):
		if value not in [str,unicode]:
			value=str(value)
		if self._doc!=None:
			try:
				self._doc.text=value
			except:
				self._doc.html=txt2html(value)
		self.location=(0,len(self.text))
				
	@property
	def html(self):
		if self._doc!=None:
			try:
				return self._doc.html
			except:
				try:
					return txt2html(self._doc.txt)
				except:
					return self._doc.__repr__()
		return self._html
	@html.setter
	def html(self,value):
		if value not in [str,unicode]:
			value=str(value)
		if self._doc!=None:
			try:
				self._doc.html=value
			except:
				self._doc.txt=html2txt(value)
		
	#def __new__(cls,doc=None,parent=None):
	#	"""
	#	required to extend str
	#	"""
	#	return super(DocFrag,cls).__new__(cls,'')
	#	#return super().__new__(cls,'') # python 3
		
	def clearCache(self):
		"""
		clear caches you don't need anymore to free up some memory
		"""
		self._words=None
		self._sentences=None
		self._paragraphs=None
		if self.children!=None:
			for c in self.children:
				c.clearCache()
	
	# I can go down this road and ensure children[] is read-only
	# but that seems wrong to me.  May be better to add hooks to the
	# array to do something on change.
	#@property
	#def children(self):
	#	return NotImplementedError()
				
	def hasChildren(self):
		return self.children!=None
	
	def __iter__(self):
		return self.children.__iter__()
		
	def __len__(self):
		return self.location[1]-self.location[0]
		
	def __repr__(self):
		return self.text
	#-------------- string methods
	def lower(self):
		return self.text.lower()
	def capitalize(self):
		return self.text.capitalize()
	def center(self,width,fillchar=' '):
		return self.text.center(width,fillchar)
	def count(self,sub,start=0,end=None):
		return self.text.count(sub,start,end)
	def decode(self,encoding='utf-8',errors='strict'):
		return self.text.decode(encoding,errors)
	def encode(self,encoding='utf-8',errors='strict'):
		return self.text.encode(encoding,errors)
	def endswith(self,suffix,start=0,end=None):
		return self.text.endswith(suffix,start,end)
	def expandtabs(self,tabsize=8):
		return self.text.expandtabs(tabsize)
	def find(self,sub,start=0,end=None):
		return self.text.find(sub,start,end)
	def format(self,*args,**kwargs):
		return self.text.format(*args,**kwargs)
	def index(self,sub,start=0,end=None):
		return self.text.index(sub,start,end)
	def isalnum(self):
		return self.text.isalnum()
	def isalpha(self):
		return self.text.isalpha()
	def isdigit(self):
		return self.text.isdigit()
	def islower(self):
		return self.text.islower()
	def isspace(self):
		return self.text.isspace()
	def istitle(self):
		return self.text.istitle()
	def isupper(self):
		return self.text.isupper()
	def join(self,iterable):
		return self.text.join(iterable)
	def ljust(self,width,fillchar=' '):
		return self.text.ljust(width,fillchar)
	def lower(self):
		return self.text.lower()
	def lstrip(self,chars=None):
		return self.text.lstrip(chars)
	def partition(self,sep):
		return self.text.partition(sep)
	def replace(self,old,new,count=None):
		raise NotImplementedError() # need to set the value!
		return self.text.replace(self,old,new,count)
	def rfind(self,sub,start=0,end=None):
		return self.text.rfind(sub,start,end)
	def rindex(self,sub,start=0,end=None):
		return self.text.rindex(sub,start,end)
	def rjust(self,width,fillchar=' '):
		return self.text.rjust(width,fillchar)
	def rpartition(self,sep):
		return self.text.rpartition(sep)
	def rsplit(self,sep,maxsplit=None):
		return self.text.rsplit(sep,maxsplit)
	def rstrip(self,chars=None):
		return self.text.rstrip(chars)
	def split(self,sep,maxsplit=None):
		return self.text.split(sep,maxsplit)
	def splitlines(self,keepends=False):
		return self.text.splitlines(keepends)
	def startswith(self,prefix,start=0,end=None):
		return self.text.startswith(prefix,start,end)
	def strip(self,chars=None):
		raise NotImplementedError() # need to set the value!
		return self.text.strip()
	def swapcase(self):
		return self.text.swapcase()
	def title(self):
		return self.text.title()
	def translate(self,table,deletechars=None):
		return self.text.translate(table,deletechars)
	def upper(self):
		return self.text.upper()
	def zfill(self,width):
		return self.text.zfill(width)
	def isnumeric(self):
		return self.text.isnumeric()
	def isdecimal(self):
		return self.text.isdecimal()
	# -------------- end string methods
	
	def wordAt(self,idx):
		"""
		get the word at a given index
		(useful for when you search for something, find it, and then
			want to know what it is)
		"""
		abs=self.location[0]+idx
		bisect.find_le
		for child in self.children:
			if abs<child.location[1]:
				return child.wordAt(abs-child.location[0])
		raise IndexError('index out of bounds!')
	
	def __getitem__(self,idx):
		"""
		idx can be an integer or a slice object:
			https://docs.python.org/2/c-api/slice.html
		"""
		# assume int for now
		#abs=self.location[0]+idx
		#for child in self.children:
		#	if abs<child.location[1]:
		#		return child[abs-child.location[0]]
		children=self.children
		idx=bisect.bisect_left(children,idx)
		if idx>=0:
			if idx>=len(children):
				idx=len(children)-1
			return children[idx]
		raise IndexError('index out of bounds!')
	def __setitem__(self,idx,val):
		"""
		idx can be an integer or a slice object:
			https://docs.python.org/2/c-api/slice.html
		"""
		# assume int for now
		abs=self.location[0]+idx
		for child in self.children:
			if abs<child.location[1]:
				child[abs-child.location[0]].assign(val)
		raise IndexError('index out of bounds!')
			
	def slice(self,start=0,end=None):
		"""
		get a slice of this fragment
		"""
		s=self.location[0]
		if start>0:
			s+=start
			if s>self.location[1]:
				raise IndexError()
		elif start<0:
			s=self.location[1]-start
			if s<0:
				raise IndexError()
		e=self.location[1]
		if end==None:
			pass
		elif end>0:
			e=self.location[0]+end
			if e>self.location[1]:
				raise IndexError()
		elif end<0:
			e-=end
			if e<0:
				raise IndexError()
		if e>s:
			raise IndexError()
		self.doc.text[s:e]
		
	def spellcheck(self):
		"""
		check the spelling of everything within a block of text
		"""
		pass
		
	def trunc(s,pos=75):
		"""
		truncates a block of text for readability e.g. "four score and seven years ago [...]"
		"""
		if len(s)>pos:
			return s[0:pos]+'[...]'
		return s
		
	@property
	def words(self):
		"""
		get all words related to this frag
		"""
		raise NotImplementedError()
		
	@property
	def sentences(self):
		"""
		get all sentences related to this frag
		(be it a parent sentence or child sentences)
		"""
		raise NotImplementedError()
		
	@property
	def paragraphs(self):
		"""
		get all sentences related to this frag
		(be it a parent paragraph or child paragraphs)
		"""
		raise NotImplementedError()
		
	@property	
	def chapters(self):
		"""
		get all chapters related to this frag
		(be it a parent chapter or child chapters)
		"""
		raise NotImplementedError()
		
	@property
	def assign(self,value):
		"""
		assign the text of this item to a given value
		"""
		raise NotImplementedError()
		
	@property
	def wordCount(self):
		return len(self.words)
	@property
	def sentenceCount(self):
		return len(self.sentences)
	@property
	def paragraphCount(self):
		return len(self.paragraphs)
	@property
	def chapterCount(self):
		return len(self.chapters)
		
	def wordNum(self):
		"""
		word number within sentence
		"""
		return 0
	def sentenceNum(self):
		"""
		sentence number within paragraph
		"""
		return 0
	def paragraphNum(self):
		"""
		para number within chapter
		"""
		return 0
	def chapterNum(self):
		"""
		chapter number within document
		"""
		return 0
		
	def descriptiveLocation(self,includeDocName=True):
		"""
		Returns a human-readable description of the location, as in
			In foo.text, chapter 3, paragraph 7, sentence 2, word 1
		Or if this is is a paragraph
			In foo.text, chapter 3, paragraph 7
		
		you can use includeDocName=False to disable redundant information
		if you already know what doc you're operating on
		
		NOTE: This is 1-based indexing 
			such that the first chapter is "chapter 1" not "chapter 0"
		"""
		ret=[]
		hl=self.hierarchyLocation()
		if includeDocName:
			ret.append('In '+hl[0])
		if hl[1]!=0 or hl[2]!=0 or hl[3]!=0 or hl[4]!=0:
			ret.append('chapter '+str(hl[1]+1))
			if hl[2]!=0 or hl[3]!=0 or hl[4]!=0:
				ret.append('paragraph '+str(hl[2]+1))
				if hl[3]!=0 or hl[4]!=0:
					ret.append('sentence '+str(hl[3]+1))
					if hl[4]!=0:
						ret.append('word '+str(hl[4]+1))
		elif not includeDocName:
			ret.append('In '+hl[0]) # include it anyway so we have something to show
		return ', '.join(ret)
		
	def hierarchyLocation(self):
		"""
		returns the location of this DocFrag in terms of
			[docName,chapterNo,paragraphNo,sentenceNo,wordNo]
		(NOTE: if, for example, we are talking about a paragraph,
		then sentenceNo and wordNo will always be zero!)
		"""
		myDoc=self.doc
		return [
			myDoc.name,
			self.chapterNum(),
			self.paragraphNum(),
			self.sentenceNum(),
			self.wordNum()]
			

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
				if arg[0] in ['-h','--help']:
					printhelp=True
				elif arg[0]=='--test':
					q=DocFrag(None,None)
					print dir(q)
				else:
					print 'ERR: unknown argument "'+arg[0]+'"'
			else:
				print 'ERR: unknown argument "'+arg+'"'
	if printhelp:
		print 'Usage:'
		print '  DocFrag.py [options]'
		print 'Options:'
		print '   --test ..... test the thing'