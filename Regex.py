#!/usr/bin/env
# -*- coding: utf-8 -*-
"""
Re-implementation of the re library that allows you to search
    both strings and HtmlString objects.
"""
import re as actualRe


class Regex:
    """
    Re-implementation of the re library that allows you to search
        both strings and HtmlString objects.

    This class represents a compiled Regex.
    """

    def __init__(self,pattern:str,flags:int=0):
        """
        :param pattern: the regular expression pattern
        :param flags: compile flags such as RE.DOTALL
        """
        self.regex=actualRe.compile(pattern,flags)

    def text(self,item):
        """
        :return: the text representation of any given item
            if it's an object,try to return item.text
            if it's a string or unicode,return that instead
            finally,try to call the str() operator on whatever it is
        """
        if hasattr(item,'text'):
            item=item.text
        if not isinstance(item,str):
            raise TypeError('Expected string,got '+item.__class__.__name__)
        return str(item)

    @property
    def flags(self):
        """
        return the original flags
        """
        return self.regex.flags
    @property
    def groups(self):
        """
        get the groups
        """
        return self.regex.groups
    @property
    def groupindex(self):
        """
        get the index of the group
        """
        return self.regex.groupindex
    @property
    def pattern(self):
        """
        return the original pattern
        """
        return self.regex.pattern

    def findall(self,src):
        """
        find all items that match a pattern
        """
        return self.regex.findall(self.text(src))

    def finditer(self,string,flags=0):
        """
        iterate over items that match a pattern
        """
        return self.regex.finditer(self.text(string),flags)

    def split(self,string,maxsplit=0,flags=0):
        """
        use a pattern to split a string
        """
        return self.regex.split(self.text(string),maxsplit,flags)

    def match(self,string,pos=0,endpos=-1):
        """
        match a string against a pattern
        """
        return self.regex.match(self.text(string),pos,endpos)

    def find(self,string,pos=0,endpos=-1):
        """
        find a pattern in a string
        """
        return self.search(string,pos,endpos)
    def search(self,string,pos=0,endpos=-1):
        """
        find a pattern in a string
        """
        return self.regex.search(self.text(string),pos,endpos)

    # def sub(self,repl,string,count=0,flags=0)
    # def subn(self,repl,string,count=0,flags=0)


class re:
    """
    Re-implementation of the re library that allows you to search
    both strings and HtmlString objects.

    It also contains automatic compiling/caching of regexes,which is a nice feature.
    """

    IGNORECASE=actualRe.IGNORECASE
    DOTALL=actualRe.DOTALL
    MULTILINE=actualRe.MULTILINE
    COMPILED_CACHE={}

    @staticmethod
    def compile(pattern,flags=0,cache=True):
        """
        compile a pattern to a regular expression
        """
        if not cache:
            return Regex(pattern,flags)
        if pattern not in re.COMPILED_CACHE:
            re.COMPILED_CACHE[pattern]=Regex(pattern,flags)
        return re.COMPILED_CACHE[pattern]

    @staticmethod
    def escape(pattern):
        """
        escape a string to be used literally in a regex
        """
        return actualRe.escape(pattern)

    @staticmethod
    def findall(pattern,src):
        """
        find all items that match a pattern
        """
        return re.compile(pattern).findall(src)

    @staticmethod
    def finditer(pattern,string,flags=0):
        """
        iterate over items that match a pattern
        """
        for match in re.compile(pattern).findall(string,flags):
            yield match

    @staticmethod
    def split(pattern,string,maxsplit=0,flags=0):
        """
        use a pattern to split a string
        """
        return re.compile(pattern).split(string,maxsplit,flags)

    @staticmethod
    def match(pattern,string,pos=0,endpos=-1):
        """
        match a string against a pattern
        """
        return re.compile(pattern).match(string,pos,endpos)

    @staticmethod
    def find(pattern,string,pos=0,endpos=-1):
        """
        find a pattern in a string
        """
        return re.compile(pattern).find(pattern,string,pos,endpos)
    @staticmethod
    def search(pattern,string,pos=0,endpos=-1):
        """
        find a pattern in a string
        """
        return re.compile(pattern).search(pattern,string,pos,endpos)

    @staticmethod
    def sub(pattern,repl,string,count=0,flags=0):
        """
        substitute a matching pattern
        """
        return re.compile(pattern).sub(repl,string,count,flags)
    @staticmethod
    def subn(pattern,repl,string,count=0,flags=0):
        """
        substitute a matching pattern
        """
        return re.compile(pattern).subn(repl,string,count,flags)