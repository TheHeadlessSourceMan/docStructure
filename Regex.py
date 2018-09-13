#!/usr/bin/env
# -*- coding: utf-8 -*-
"""
Re-implementation of the re library that allows you to search
	both strings and HtmlString objects.
"""
import re as actualRe


class Regex(object):
	"""
	Re-implementation of the re library that allows you to search
		both strings and HtmlString objects.
		
	This class represents a compiled Regex.
	"""
	
	def __init__(self,pattern,flags=0):
		"""
		:param pattern: the regular expression pattern
		:param flags: compile flags such as RE.DOTALL
		"""
		self.regex=actualRe.compile(pattern,flags)
		
	def text(self,item):
		"""
		:return: the text representation of any given item
			if it's an object, try to return item.text
			if it's a string or unicode, return that instead
			finally, try to call the str() operator on whatever it is
		"""
		if hasattr(item,'text'):
			item=item.text
		if type(item) not in (str,unicode):
			raise TypeError('Expected string, got '+item.__class__.__name__)
		return str(item)
		
	@property
	def flags(self):
		return self.regex.flags
	@property
	def groups(self):
		return self.regex.groups
	@property
	def groupindex(self):
		return self.regex.groupindex
	@property
	def pattern(self):
		return self.regex.pattern
		
	def findall(self,src):
		return self.regex.findall(self.text(src))
		
	def finditer(self,string,flags=0):
		return self.regex.finditer(self.text(string),flags)
		
	def split(self,string,maxsplit=0,flags=0):
		return self.regex.split(self.text(string),maxsplit,flags)
		
	def match(self,string,pos=0,endpos=-1):
		return self.regex.match(self.text(string),pos,endpos)
		
	def find(self,string,pos=0,endpos=-1):
		return self.search(string,pos,endpos)
	def search(self,string,pos=0,endpos=-1):
		return self.regex.search(self.text(string),pos,endpos)
	
	# def sub(self, repl, string, count=0, flags=0)	
	# def subn(self, repl, string, count=0, flags=0)
	
	
class re:
	"""
	Re-implementation of the re library that allows you to search
	both strings and HtmlString objects.
	
	It also contains automatic compiling/caching of regexes, which is a nice feature.
	"""
	
	IGNORECASE=actualRe.IGNORECASE
	DOTALL=actualRe.DOTALL
	MULTILINE=actualRe.MULTILINE
	COMPILED_CACHE={}
	
	@staticmethod
	def compile(pattern,flags=0,cache=True):
		if not cache:
			return Regex(pattern,flags)
		if pattern not in re.COMPILED_CACHE:
			re.COMPILED_CACHE[pattern]=Regex(pattern,flags)
		return re.COMPILED_CACHE[pattern]
		
	@staticmethod
	def escape(pattern):
		return actualRe.escape(pattern)
		
	@staticmethod
	def findall(pattern,src):
		return re.compile(pattern).findall(src)
		
	@staticmethod
	def finditer(pattern,string,flags=0):
		return re.compile(pattern).findall(string,flags)
		
	@staticmethod
	def split(pattern,string,maxsplit=0,flags=0):
		return re.compile(pattern).split(string,maxsplit,flags)
		
	@staticmethod
	def match(pattern,string,pos=0,endpos=-1):
		return re.compile(pattern).match(string,pos,endpos)
		
	@staticmethod
	def find(pattern,string,pos=0,endpos=-1):
		return re.compile(pattern).find(pattern,string,pos,endpos)
	@staticmethod
	def search(pattern,string,pos=0,endpos=-1):
		return re.compile(pattern).search(pattern,string,pos,endpos)
	
	@staticmethod
	def sub(pattern,repl,string,count=0,flags=0):
		return re.compile(pattern).sub(repl,string,count,flags)
	@staticmethod
	def subn(pattern,repl,string,count=0,flags=0):
		return re.compile(pattern).subn(repl,string,count,flags)