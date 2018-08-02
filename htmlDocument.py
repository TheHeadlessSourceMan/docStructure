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

	def __init__(self,parent,titleNode,contentNodes):
		Chapter.__init__(self,parent,parent)
		print 'WWWWWWWW',type(self.parent),self.parent.dataProvider
		self.titleNode=titleNode
		self.contentNodes=contentNodes
		self.set(None,self.text)
		
	@property
	def title(self):
		return self.titleNode.text
	@title.setter
	def title(self,title):
		self.titleNode.text=title
		
	@property
	def text(self):
		ret=[]
		for node in self.contentNodes:
			if type(node)==lxml.etree._ElementStringResult:
				val=node
			elif type(node)==lxml.etree._ElementUnicodeResult:
				val=unicode(node) # errors='replace' is unnecessary because it is valid unicode
			elif type(node)==lxml.html.HtmlComment:
				continue
			else:
				if node.tag in ['h1','h2','h3','h4']:
					continue
				val=lxml.etree.tostring(node,encoding='UTF-8',method="text")
				if node.tag in ['br','p','hr']:
					val=val+'\n'
				elif node.tag not in ['i','u','b']:
					print 'Unknown tag',node.tag
					raise Exception()
			if type(val)!=unicode:
				val=unicode(val,errors='replace')
			ret.append(val)
		return ''.join(ret)
		

class HtmlDocument(DocumentBase):
	"""
	This allows opening html as a word processor document, and/or serves as an example for implementing other formats.
	"""
	
	def __init__(self,filename=None,html=None):
		DocumentBase.__init__(self)
		self._children=None
		self._wrapped=None
		self._filename=None
		TODO: here is the problem.  I have this dataProvider scheme that the child DocFrags want to use to get
		text to parse, but this class reads the html file directly.  Something about this scheme is convoluded
		and all-around bad.
		self._dataProvider=self
		self.load(filename,html)
		
	def load(self,filename=None,html=None,mimeType=None):
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
		ret=[]
		for c in self.chapters:
			ret.append(c.title)
			ret.append(len(c.title)*'-')
			ret.append(c.text)
			ret.append('')
		return '\n'.join(ret)
		
	def _chapterSplit(self,element,headingLevel='h1'):
		"""
		Parse a document into chapters such as:
			<h2>chapter title</h2>
			chapter contents
			<h2>next chapter title</h2>
			...
		
		It is designed such that someday you can have different heading levels
			for an engineering style document
		"""
		ret=[]
		nodes=self.etree.xpath('//*/'+headingLevel)
		for i in range(len(nodes)):
			titleNode=nodes[i]
			#print 'FOUND',titleNode.text
			xpath='/html/body/'+headingLevel+'['+str(i+1)+']/following-sibling::node()[not(self::h1)][count(preceding-sibling::'+headingLevel+')='+str(i+1)+']'
			contentNodes=self.etree.xpath(xpath)
			ret.append((titleNode,contentNodes))
		return ret
		
	@property
	def children(self):
		if self._children==None:
			self._children=[]
			body=self.etree.xpath('//*/body')[0]
			for level in range(9): # first check <h1> then <h2> and so on until we get something split
				chapters=self._chapterSplit(body,'h'+str(level))
				if len(chapters)>0:
					for title,contents in chapters:
						self._children.append(HtmlChapter(self,title,contents))
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