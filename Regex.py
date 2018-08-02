#!/usr/bin/env
# -*- coding: utf-8 -*-
"""
Re-implementation of the re library that allows you to search
	both strings and HtmlString objects.
"""
import re as actualRe


class Regex(object):
	
	def __init__(self,pattern,flags=0):
		self.regex=actualRe.compile(pattern,flags)
		
	def text(self,item):
		if hasattr(item,'text'):
			item=item.text
		if type(item) not in (str,unicode):
			raise TypeError('Expected string, got '+item.__class__.__name__)
		return item
		
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
	
	# def sub(self, repl, string, count=0, flags=0)	
	# def subn(self, repl, string, count=0, flags=0)
	
	
class re:
	"""
	Re-implementation of the re library that allows you to search
	both strings and HtmlString objects.
	"""
	
	IGNORECASE=actualRe.IGNORECASE
	DOTALL=actualRe.DOTALL
	MULTILINE=actualRe.MULTILINE
	
	@staticmethod
	def compile(pattern,flags=0):
		return Regex(pattern,flags)
		
	@staticmethod
	def escape(pattern):
		return actualRe.escape(pattern)
		
	def findall(pattern,src):
		return Regex(pattern).findall(src)
		
	def finditer(pattern,string,flags=0):
		return Regex(pattern).findall(string,flags)
		
	def split(pattern,string,maxsplit=0,flags=0):
		return Regex(pattern).split(string,maxsplit,flags)
	
	# re.sub(pattern, repl, string, count=0, flags=0)	
	# re.subn(pattern, repl, string, count=0, flags=0)


