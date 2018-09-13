#!/usr/bin/env
# -*- coding: utf-8 -*-
"""
This allows opening html as a word processor document, and/or serves as an example for implementing other formats.
"""
if False:
	from docStructure import Document
	from docStructure import Chapter
else:
	from Document import DocumentBase
	from Chapter import Chapter
	from DocFrag import * 
import lxml.html,lxml.etree


class HtmlChapter(Chapter):
	"""
	Figure out how a chapter looks in an html document
	"""

	def __init__(self,parent,titleNode,contentNodes,position):
		"""
		:param parent: the parent object in the hierarchy
		:param titleNode: xml node containing the chapter title
		:param contentNodes: xml nodes containing the guts of the chapter
		:param position: the actual location of this item
		"""
		Chapter.__init__(self,parent,parent,position)
		self._text=None
		self.titleNode=titleNode
		self.contentNodes=contentNodes
		self.set(None,self.text)
		
	@property
	def position(self):
		"""
		Override position so we can base it on the text length.
		
		TODO: I'm not sure I like doing it this way.
		"""
		return (self._position[0],len(self))
	@position.setter
	def position(self,position):
		self._position=position
		
	@property
	def title(self):
		return self.titleNode.text
	@title.setter
	def title(self,title):
		self.titleNode.text=title
		
	def __len__(self):
		return len(self.text)
		
	@property
	def text(self):
		"""
		Get plaintext representation.
		"""
		if self._text==None:
			ret=[]
			for node in self.contentNodes:
				if type(node)==lxml.etree._ElementStringResult:
					val=node
				elif type(node)==lxml.etree._ElementUnicodeResult:
					val=unicode(node) # errors='replace' is unnecessary because it is valid unicode
				elif type(node)==lxml.html.HtmlComment:
					continue
				else:
					if node.tag[0]=='h' and node.tag[1].isdigit():
						continue
					val=lxml.etree.tostring(node,encoding='UTF-8',method="text")
					if node.tag in ['pre','br','p','hr','table','tr','div']: # assume div is a block element
						val=val+'\n'
					elif node.tag not in ['i','u','b','td']:
						print 'Unknown tag',node.tag
						raise Exception()
				if type(val)!=unicode:
					val=unicode(val,errors='replace')
				ret.append(val)
			self._text=''.join(ret)
		return self._text
		

class HtmlDocument(DocumentBase):
	"""
	This allows opening html as a word processor document, and/or serves as an example for implementing other formats.
	
	
	TODO: here is the problem.  I have this dataProvider scheme that the child DocFrags want to use to get
		text to parse, but this class reads the html file directly.  Something about this scheme is convoluted
		and all-around bad.
	"""
	
	def __init__(self,filename=None,html=None):
		"""
		:param filename: can be a filename or common form of url. SEE Load()
		:param html: if you want to feed in the document's html directly rather than loading it
		"""
		DocumentBase.__init__(self)
		self._text=None
		self._children=None
		self._wrapped=None
		self._filename=None
		self._dataProvider=self
		self.load(filename,html)
		
	def load(self,filename=None,html=None):
		"""
		Load document data.
		
		:param filename: can be:
			* a docStructure.Document derived object
			* a file name
			* a URL
			* a file-like object
			* '-' to specify stdin
			* None if data is to be passed in instead
		:param html: if filename is None, pass in a data buffer
		"""
		self.etree=None
		if hasattr(filename,'html') or 'html' in dir(filename):
			# looks like we're wrapping it
			self._wrapped=filename
			self._filename=None
			html=self._wrapped.html
		else:
			self._filename=filename
			if html==None:
				if filename!=None:
					f=open(filename,'rb')
					html=f.read().replace('\r\n','\n') # windows line endings are lame
					f.close()
				else:
					return
			if hasattr(html,'html'):
				html=html.html
		self.etree=lxml.html.fromstring(html.replace('\n',' '))
		
	def save(self,asFilename=None):
		"""
		asFilename can be:
			* None to save over existing
			* an html filename
			* any file type a wrapped object supports
			* a file-like object (if non-wrapped)
			* "-" for stdout (if non-wrapped)
		"""
		if (asFilename==None or asFilename.rsplit('.',1)[-1] not in ['htm','html','xhtml']) and	self._wrapped!=None and hasattr(self._wrapped,'filename'):
			return self._wrapped.filename.save(asFilename)
		else:
			if asFilename==None:
				asFilename=self.filename
			elif hasattr(asFilename,'write'):
				asFilename.write(self.html)
			elif asFilename=='-':
				print self.html
			else:
				f=open(asFilename,'wb')
				f.write(self.html)
				f.close()
		
	@property
	def filename(self):
		"""
		:return: the current filename, or None if there isn't one
		"""
		if self._wrapped!=None and hasattr(self._wrapped,'filename'):
			return self._wrapped.filename
		return self._filename
		
	@property
	def html(self):
		return lxml.etree.tostring(self.etree,pretty_print=True)
	@html.setter
	def html(self,html):
		if self._wrapped!=None:
			self._wrapped.html=html
		else:
			self.load(text=html)
		
	@property
	def text(self):
		"""
		:return: the contents re-formatted as text
		"""
		if self._text==None:
			ret=[]
			i=1
			for c in self.chapters:
				title=c.title
				if title==None:
					title='Chapter '+str(i)
				ret.append(title)
				ret.append(len(title)*'-')
				ret.append(c.text)
				ret.append('')
				i+=1
			self._text='\n'.join(ret)
		return self._text
		
	def _chapterSplit(self,element,headingLevel='h1'):
		"""
		Helper function to split a document into chapters when formatted such as:
			<h2>chapter title</h2>
			chapter contents
			<h2>next chapter title</h2>
			...
		
		It is designed such that someday you can have different heading levels
			for an engineering style document
			
		:param element: the starting xml element
		:param headingLevel: the level we are operating at
		"""
		ret=[]
		nodes=self.etree.xpath('//*/'+headingLevel)
		for i in range(len(nodes)):
			titleNode=nodes[i]
			#print 'FOUND',titleNode.text
			xpath='/html/body/'+headingLevel+'['+str(i+1)+']/following-sibling::node()[not(self::'+headingLevel+')][count(preceding-sibling::'+headingLevel+')='+str(i+1)+']'
			contentNodes=element.xpath(xpath)
			ret.append((titleNode,contentNodes))
		return ret
		
	@property
	def children(self):
		"""
		splits children (aka chapters) from the html doc
		"""
		if self._children==None:
			self._children=[]
			body=self.etree.xpath('//*/body')[0]
			position=[0,0]
			for level in range(9): # first check <h1> then <h2> and so on until we get something split
				chapters=self._chapterSplit(body,'h'+str(level))
				if len(chapters)>0:
					for title,contents in chapters:
						chap=HtmlChapter(self,title,contents,position)
						self._children.append(chap)
						position[0]+=len(chap)
					break
		return self._children


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
				else:
					print 'ERR: unknown argument "'+arg[0]+'"'
			else:
				print 'ERR: unknown argument "'+arg+'"'
	if printhelp:
		print 'Usage:'
		print '  htmlDocument.py [options]'
		print 'Options:'
		print '   NONE'