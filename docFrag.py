#!/usr/bin/env
# -*- coding: utf-8 -*-
"""
This is the base class for all Document components (Word,Paragraph,etc)
"""
import typing
import bisect # binary searching to speed things up
from pynode import Node
from docStructure import Location
if typing.TYPE_CHECKING:
    from docStructure import Word, Chapter, Paragraph, Sentence, Section


class DocFrag(Node,Location):#(str,Node,Location):
    """
    This is the base class for all Document components (Word,Paragraph,etc)
    """

    #def __new__(cls,doc,parent,position=0):
    #    obj=str.__new__(cls,'') # initialization of str metaclass
    #    #obj=Node.__new__(cls,cls.__name__,parent=parent)
    #    return obj

    frag=''

    def __init__(self,doc,parent:"DocFrag",position:int=0):
        """
        :param doc: the document this paragraph belongs to
        :param parent: the parent object in the hierarchy
        :param position: the actual location of this item
        """
        Node.__init__(self,self.__class__.__name__,parent=parent)
        Location.__init__(self,doc,position)
        self._html:typing.Optional[str]=None
        self._dataProvider:typing.Optional[str]=None # actual data this comes from
        self._words:typing.Optional[typing.List["DocFrag"]]=None # a cache
        self._sentences:typing.Optional[typing.List["DocFrag"]]=None # a cache
        self._paragraphs:typing.Optional[typing.List["DocFrag"]]=None # a cache
        self.include:bool=True # use this to skip a doc frag when compiling document

    @property
    def json(self):
        ret={
            'frag':self.frag
        }
        if hasattr(self,'title'):
            if self.title is None:
                ret['title']=''
            else:
                ret['title']=self.title
        children=[ch.json for ch in self.children]
        if children:
            ret['children']=children
        return ret
    @property
    def jsonString(self):
        from json import dumps
        return dumps(self.json)

    @property
    def parent(self)->"DocFrag":
        """
        get the parent fragment
        """
        return self._parent
    @parent.setter
    def parent(self,parent):
        self._parent=parent

    @property
    def root(self)->"DocFrag":
        """
        the root of the document
        """
        r=self
        while self.parent is not None and self.parent is not self:
            r=self.parent
        return r

    @property
    def dataProvider(self):
        """
        retrieve the data provider that generated this docfrag
        """
        if self._dataProvider is not None:
            ret=self._dataProvider
        else:
            ret=self.parent.dataProvider
            if ret is None:
                ret=self.doc
        if ret is None:
            raise Exception(self.__class__.__name__+' - dataProvider has gone missing!!!')
        return ret

    @property
    def text(self)->str:
        """
        get plain text of this docfrag
        """
        text=''
        dataProvider=self.dataProvider
        if dataProvider is not None:
            text=dataProvider.text
            if text is None:
                text=''
            #elif isinstance(text,basestring):
            #    text=unicode(text,errors='replace')
        if self.position is not None:
            text=text[self.position[0]:self.position[1]]
        return text
    @text.setter
    def text(self,value:str):
        """
        assign the docfrag to a body of text
        """
        if not isinstance(value,str):
            value=str(value)
        if self.doc is not None:
            try:
                self.doc.text=value
            except Exception:
                from docStructure import txt2html
                self.doc.html=txt2html(value)
        self.position=(0,len(self.text))

    @property
    def html(self)->str:
        """
        get the docfrag as formatted html
        """
        if self._html is not None:
            try:
                return self.doc.html
            except Exception:
                try:
                    from docStructure import txt2html
                    return txt2html(self.doc.txt)
                except Exception:
                    return self.doc.__repr__()
        elif self.text is not None:
            from docStructure import txt2html
            return txt2html(self.text)
        return self._html
    @html.setter
    def html(self,value:str):
        """
        assign the docfrag to a piece of html
        """
        if value not in [str,str]:
            value=str(value)
        if self.doc is not None:
            try:
                self.doc.html=value
            except Exception:
                from docStructure import html2txt
                self.doc.txt=html2txt(value)

    #def __new__(cls,doc=None,parent=None):
    #    """
    #    required to extend str
    #    """
    #    return super(DocFrag,cls).__new__(cls,'')
    #    #return super().__new__(cls,'') # python 3

    def clearCache(self)->None:
        """
        clear caches you don't need anymore to free up some memory
        """
        self._words=None
        self._sentences=None
        self._paragraphs=None
        if self.children is not None:
            for c in self.children:
                c.clearCache()

    def hasChildren(self)->bool:
        """
        returns whether this item has children or not
        """
        return self.children is not None and self.children

    def __iter__(self)->typing.Iterator["DocFrag"]:
        # TODO: this does not work, and I don't know why I was doing it anyway
        #if not hasattr(self,'children'):
        #    print('ERR: No member "children" for '+self.__class__.__name__,dir(self))
        return self.children.__iter__()

    def __str__(self)->str:
        return self.text

    #-------------- string methods
    def capitalize(self)->None:
        """
        string method
        """
        return self.text.capitalize()
    def center(self,width:int,fillchar:str=' ')->str:
        """
        string method
        """
        return self.text.center(width,fillchar)
    def count(self,sub:str,start:int=0,end:typing.Optional[int]=None)->int: # pylint: disable=arguments-differ
        """
        string method
        """
        return self.text.count(sub,start,end)
    def decode(self,encoding:str='utf-8',errors:str='strict')->str:
        """
        string method
        """
        return self.text.decode(encoding,errors)
    def encode(self,encoding:str='utf-8',errors:str='strict')->bytes:
        """
        string method
        """
        return self.text.encode(encoding,errors)
    def endswith(self,suffix:str,start:int=0,end:typing.Optional[int]=None)->bool:
        """
        string method
        """
        return self.text.endswith(suffix,start,end)
    def expandtabs(self,tabsize:str=8)->str:
        """
        string method
        """
        return self.text.expandtabs(tabsize)
    def find(self,sub:str,start:int=0,end:typing.Optional[int]=None)->int:
        """
        string method
        """
        return self.text.find(sub,start,end)
    def format(self,*args,**kwargs)->str:
        """
        string method
        """
        return self.text.format(*args,**kwargs)
    def index(self,value:str,start:int=0,stop:typing.Optional[int]=None)->int:
        """
        string method
        """
        return self.text.index(value,start,stop)
    def isalnum(self)->bool:
        """
        string method
        """
        return self.text.isalnum()
    def isalpha(self)->bool:
        """
        string method
        """
        return self.text.isalpha()
    def isdigit(self)->bool:
        """
        string method
        """
        return self.text.isdigit()
    def islower(self)->bool:
        """
        string method
        """
        return self.text.islower()
    def isspace(self)->bool:
        """
        string method
        """
        return self.text.isspace()
    def istitle(self)->bool:
        """
        string method
        """
        return self.text.istitle()
    def isupper(self)->bool:
        """
        string method
        """
        return self.text.isupper()
    def join(self,iterable:typing.Iterable[typing.Any])->str:
        """
        string method
        """
        return self.text.join(iterable)
    def ljust(self,width:int,fillchar:str=' ')->str:
        """
        string method
        """
        return self.text.ljust(width,fillchar)
    def lower(self)->str:
        """
        string method
        """
        return self.text.lower()
    def lstrip(self,chars:typing.Optional[str]=None)->str:
        """
        string method
        """
        return self.text.lstrip(chars)
    def partition(self,sep:str)->str:
        """
        string method
        """
        return self.text.partition(sep)
    def replace(self,old:str,new:str,count:typing.Optional[int]=None)->str:
        """
        string method
        """
        return self.text.replace(old,new,count)
    def rfind(self,sub:str,start:int=0,end:typing.Optional[int]=None)->int:
        """
        string method
        """
        return self.text.rfind(sub,start,end)
    def rindex(self,sub:str,start:int=0,end:typing.Optional[str]=None)->int:
        """
        string method
        """
        return self.text.rindex(sub,start,end)
    def rjust(self,width,fillchar=' '):
        """
        string method
        """
        return self.text.rjust(width,fillchar)
    def rpartition(self,sep):
        """
        string method
        """
        return self.text.rpartition(sep)
    def rsplit(self,sep,maxsplit=None):
        """
        string method
        """
        return self.text.rsplit(sep,maxsplit)
    def rstrip(self,chars=None):
        """
        string method
        """
        return self.text.rstrip(chars)
    def split(self,sep,maxsplit=-1):
        """
        string method
        """
        return self.text.split(sep,maxsplit)
    def splitlines(self,keepends=False):
        """
        string method
        """
        return self.text.splitlines(keepends)
    def startswith(self,prefix,start=0,end=None):
        """
        string method
        """
        return self.text.startswith(prefix,start,end)
    def strip(self,chars=None):
        """
        string method
        """
        return self.text.strip(chars)
    def swapcase(self):
        """
        string method
        """
        return self.text.swapcase()
    # This method is rarely used and tends to conflict with doc/chapter titles
    #def title(self):
    #    """
    #    string method
    #    """
    #    return self.text.title()
    def translate(self,table,deletechars=None):
        """
        string method
        """
        return self.text.translate(table,deletechars)
    def upper(self):
        """
        string method
        """
        return self.text.upper()
    def zfill(self,width):
        """
        string method
        """
        return self.text.zfill(width)
    def isnumeric(self):
        """
        string method
        """
        return self.text.isnumeric()
    def isdecimal(self):
        """
        string method
        """
        return self.text.isdecimal()
    # -------------- end string methods

    def wordAt(self,idx):
        """
        get the word at a given index
        (useful for when you search for something,find it,and then
            want to know what it is)
        """
        absoluteLocation=self.position[0]+idx
        for child in self.children:
            if absoluteLocation<child.position[1]:
                return child.wordAt(absoluteLocation-child.position[0])
        raise IndexError('index out of bounds!')

    def __getitem__(self,idx):
        """
        idx can be an integer or a slice object:
            https://docs.python.org/2/c-api/slice.html
        """
        # assume int for now
        #abs=self.position[0]+idx
        #for child in self.children:
        #    if abs<child.position[1]:
        #        return child[abs-child.position[0]]
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
        absoluteLocation=self.position[0]+idx
        for child in self.children:
            if absoluteLocation<child.position[1]:
                child[absoluteLocation-child.position[0]].assign(val)
        raise IndexError('index out of bounds!')

    def slice(self,start=0,end=None):
        """
        get a slice of this fragment
        """
        s=self.position[0]
        if start>0:
            s+=start
            if s>self.position[1]:
                raise IndexError()
        elif start<0:
            s=self.position[1]-start
            if s<0:
                raise IndexError()
        e=self.position[1]
        if end is None:
            pass
        elif end>0:
            e=self.position[0]+end
            if e>self.position[1]:
                raise IndexError()
        elif end<0:
            e-=end
            if e<0:
                raise IndexError()
        if e>s:
            raise IndexError()
        return self.doc.text[s:e]

    def spellcheck(self):
        """
        check the spelling of everything within a block of text
        """

    def trunc(self,s,pos=75):
        """
        truncates a block of text for readability e.g. "four score and seven years ago [...]"
        """
        if len(s)>pos:
            return s[0:pos]+'[...]'
        return s

    def assign(self,value:str)->None:
        """
        assign the text of this item to a given value
        """
        self.set((0,0),value)

    def findChildren(self,fragType:typing.Optional[str]=None
        )->typing.Generator["DocFrag",None,None]:
        """
        deapth-first traversal
        """
        for ch in self.children:
            if fragType is None or fragType==ch.frag:
                yield ch
            yield from ch.findChildren(fragType)
    def findParent(self,fragType:typing.Optional[str]=None)->typing.Optional["DocFrag"]:
        if self.parent is None:
            return None
        if fragType is None or self.parent.frag==fragType:
            return self.parent
        return self.parent.findParent(fragType)


    @property
    def words(self)->typing.Iterable["Word"]:
        return iter(self.findChildren('word'))
    @property
    def chapters(self)->typing.Iterable["Chapter"]:
        return iter(self.findChildren('chapter'))
    @property
    def paragraphs(self)->typing.Iterable["Paragraph"]:
        return iter(self.findChildren('paragraph'))
    @property
    def sentences(self)->typing.Iterable["Sentence"]:
        return iter(self.findChildren('sentence'))
    @property
    def sections(self)->typing.Iterable["Section"]:
        return iter(self.findChildren('section'))

    @property
    def wordCount(self)->int:
        """
        how many words are associated with this doc frag
        """
        return len(self.findChildren('word'))
    numWords=wordCount
    @property
    def sentenceCount(self)->int:
        """
        how many sentences are associated with this doc frag
        """
        return len(self.findChildren('sentence'))
    numSentences=sentenceCount
    @property
    def paragraphCount(self)->int:
        """
        how many paragraphs are associated with this doc frag
        """
        return len(self.findChildren('paragraph'))
    numParagraphs=paragraphCount
    @property
    def chapterCount(self)->int:
        """
        how many chapters are associated with this doc frag
        """
        return len(self.findChildren('chapter'))
    numChapters=chapterCount

    def descriptiveLocation(self,includeDocName:bool=True)->str:
        """
        Returns a human-readable description of the location,as in
            In foo.text,chapter 3,paragraph 7,sentence 2,word 1
        Or if this is is a paragraph
            In foo.text,chapter 3,paragraph 7

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
        return ','.join(ret)

    def hierarchyLocation(self)->typing.Tuple[str,int,int,int,int]:
        """
        returns the location of this DocFrag in terms of
            [docName,chapterNo,paragraphNo,sentenceNo,wordNo]
        (NOTE: if,for example,we are talking about a paragraph,
        then sentenceNo and wordNo will always be zero!)
        """
        myDoc=self.doc
        return (
            myDoc.name,
            self.chapterNum(),
            self.paragraphNum(),
            self.sentenceNum(),
            self.wordNum())


def cmdline(args:typing.Iterable[str])->int:
    """
    Run the command line

    :param args: command line arguments (WITHOUT the filename)
    """
    printhelp=False
    if not args:
        printhelp=True
    else:
        for arg in args:
            if arg.startswith('-'):
                arg=[a.strip() for a in arg.split('=',1)]
                if arg[0] in ['-h','--help']:
                    printhelp=True
                elif arg[0]=='--test':
                    pass #_=DocFrag(None,None,None)
                else:
                    print('ERR: unknown argument "'+arg[0]+'"')
            else:
                print('ERR: unknown argument "'+arg+'"')
    if printhelp:
        print('Usage:')
        print('  DocFrag.py [options]')
        print('Options:')
        print('   --test ..... test the thing')


if __name__=='__main__':
    import sys
    cmdline(sys.argv[1:])