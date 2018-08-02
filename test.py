#!/usr/bin/env
# -*- coding: utf-8 -*-
"""
This program
"""
import bs4 as bs
from Regex import *
		
		
class HtmlString(object):
	"""
	A string object implementation that allows you to perform string ops
	in-place on an html document.
	"""
	
	def __init__(self,sources,start=0,end=None):
		"""
		sources - can be:
			* a file-like object
			* a BeautifulSoup object
			* a text buffer representing raw html
			* a single html tag
			* TODO: any object with an html data member
				(must be able to get+set for full functionality!)
			* TODO: an array of any of these
			
		start,end - clip the source (functions the same as an array slice)
		
		see also:
			https://youkilljohnny.blogspot.com/2014/03/beautifulsoup-cheat-sheet-parse-html-by.html
		"""
		self.start=start
		self.end=end
		if type(sources)!=list:
			sources=[sources]
		self.sources=sources
		self._text=None
		if isinstance(source,bs.BeautifulSoup):
			self.soup=source.body
		elif isinstance(source,bs.Tag):
			self.soup=source
		else:
			self.soup=bs.BeautifulSoup(source,'lxml').body
			
	@property
	def title(self):
		for s in self.sources:
			if type(s)==bs.BeautifulSoup:
				if s.title!=None:
					return s.title.text
			elif hasattr(s,'title'):
				return s.title
			
	def getHtmlSlice(self,idx):
		start=self.start+idx.start
		end=self.end+idx.stop
		return HtmlString(self.source,start,end)
			
	def __getitem__(self,idx):
		ezMode=True
		if ezMode:
			return self.text[idx]
		else:
			if not hasattr(self.soup,'len'):
				self._calcTextSize()
			if type(idx)==int:
				if idx<0:
					idx+=self.soup.end_idx
				n=self.leastCommonNode(idx,idx+1)
				if not isinstance(n,bs.NavigableString):
					return n.text[idx-n.start_idx]
				return n[idx-n.start_idx]
			# idx is a slice
			start=idx.start
			end=idx.stop
			if end==None:
				end=self.soup.end_idx
			elif end<0:
				end+=self.soup.end_idx
			if start==None:
				start=0
			elif start<0:
				start+=self.soup.end_idx
			n=self.leastCommonNode(start,end)
			if not isinstance(n,bs.NavigableString):
				return n.text[start-n.start_idx:end-n.start_idx:idx.step]
			return n[start-n.start_idx:end-n.start_idx:idx.step]
		
	def __setitem__(self,idx,val):
		ezMode=self._text
		if not hasattr(self.soup,'len'):
			self._calcTextSize()
		if type(idx)==int:
			if idx<0:
				idx+=self.soup.end_idx
			n=self.leastCommonNode(idx,idx+1)
			if not isinstance(n,bs.NavigableString):
				start=idx
				end=idx+1
			else:
				start=idx
				end=idx+1
		else: # idx is a slice
			start=idx.start
			end=idx.stop
			if end==None:
				end=self.soup.end_idx
			elif end<0:
				end+=self.soup.end_idx
			if start==None:
				start=0
			elif start<0:
				start+=self.soup.end_idx
			n=self.leastCommonNode(start,end)
		if not isinstance(n,bs.NavigableString):
			n.text=n.text[0:start-n.start_idx]+val+n.text[start-n.end_idx:]
			self._markNodeDirty(n)
		else:
			n.assign(n[0:start-n.start_idx]+val+n[end-n.start_idx:])
			self._markNodeDirty(n)
		if ezMode!=None:
			self._text=ezMode[0:start]+val+ezMode[end:]
		
	def __get_navigable_strings(self,soup=None):
		if soup==None:
			soup=self.soup
		if isinstance(soup,bs.NavigableString):
			if type(soup) not in (bs.Comment, bs.Declaration) and soup.strip():
				yield soup
		elif soup.name not in ('script', 'style'):
			for c in soup.contents:
				for g in self.__get_navigable_strings(c):
					yield g 
					
	def _recalc(self,soup=None,start_idx=0,force=False):
		if soup==None:
			soup=self.soup
		if force or not hasattr(soup,'dirty') or soup.dirty==True:
			soup.start_idx=start_idx
			total=0
			for node in soup.children:
				if not hasattr(node,'dirty') or node.dirty==True:
					force=True # cause siblings to be recalculated
				if isinstance(node,bs.NavigableString):
					if type(node) not in (bs.Comment, bs.Declaration):
						node.start_idx=soup.start_idx+total
						if not hasattr(node,'dirty') or node.dirty==True:
							node.len=node.__len__()
						total+=node.len
						node.end_idx=soup.start_idx+total
						node.dirty=False
					else:
						node.start_idx=soup.start_idx+total
						node.len=0
						node.end_idx=node.start_idx
						node.dirty=False
				else:
					total+=self._recalc(node,start_idx+total,force)
			soup.len=total
			soup.end_idx=soup.start_idx+total
			soup.dirty=False
		return self.end_idx-self.start_idx
		
	def __len__(self):
		return self._recalc()
		
	def setTag(self,idx,name,attrs={},status=True):
		"""
		status = True to insert a tag, False to remove it
		
		Will throw an exception when setting:
			setTag(0:8,'div',{'id':'newid'})
		into:
			this<div id="oldid">that not that</div>
		Because id=newid cannot be split, nor can id=oldid 
		
		"""
		unique='id' in attrs # decide if the new tag can be split
		raise NotImplementedError()
		
	def underline(self,idx,status=True):
		self.setTag(idx,'u',status=True)
		
	def bold(self,idx,status=True):
		self.setTag(idx,'b',status=True)
		
	def italic(self,idx,status=True):
		self.setTag(idx,'i',status=True)
		
	def _markNodeDirty(self,node):
		"""
		mark a node (and its dependencies) dirty
		"""
		self._text=None
		while True:
			node.dirty=True
			if not isinstance(node.parent,bs.Tag):
				break
			node=node.parent
		
	def leastCommonNode(self,start=0,end=None,soup=None):
		if soup==None:
			soup=self.soup
		self._recalc()
		if end==None:
			end=soup.end_idx
		elif end<0:
			end+=soup.end_idx
		if end>soup.end_idx or end<0:
			raise IndexError()
		if start==None:
			start=0
		elif start<0:
			start+=soup.end_idx
		if start>soup.end_idx or start<0:
			raise IndexError()
		# see if there is a child node that encompasses this search
		if hasattr(soup,'children'):
			for node in soup.children:
				if start>=node.start_idx and end<=node.end_idx:
					return self.leastCommonNode(start,end,node)
		# this node is the lowest common denominator
		return soup
			
	def find(self,sub,start=0,end=None):
		return self.text.find(sub)
		
	def ifind(self,sub,start=0,end=None):
		return self.text.ifind(sub)
		
	@property
	def html(self):
		return str(self.soup)
		
	@property
	def text(self):
		if self._text==None:
			self._text=self.soup.text
		return self._text
		
	def __str__(self):
		return self.html


regex=r"""\s+Hard\s+"""
regex=re.compile(regex,re.IGNORECASE)
filename='examples\\hard2parse.html'
f=open(filename,'rb')
s=HtmlString(f)


