#!/usr/bin/env
# -*- coding: utf-8 -*-
"""
This is the base class for all Document components (Word,Paragraph,etc)
"""
import typing
import bisect # binary searching to speed things up
from htmlTools import HtmlCompatible,TextCompatible
from pynode import Node
from docStructure import Location
if typing.TYPE_CHECKING:
    from .word import Word
    from .chapter import Chapter
    from .paragraph import Paragraph
    from .sentence import Sentence
    from .section import Section
    from .document import Document
    from .comment import Comment


class DocFrag(Node["DocFrag"],Location):#(str,Node,Location):
    """
    This is the base class for all Document components (Word,Paragraph,etc)
    """

    #def __new__(cls,doc,parent,position=0):
    #    obj=str.__new__(cls,'') # initialization of str metaclass
    #    #obj=Node.__new__(cls,cls.__name__,parent=parent)
    #    return obj

    frag:str=''

    def __init__(self,doc:"Document",parent:"DocFrag",startPosition:int=0):
        """
        :param doc: the document this paragraph belongs to
        :param parent: the parent object in the hierarchy
        :param startPosition: the actual location of this item
        """
        Node.__init__( # type: ignore
            self,self.__class__.__name__,parent=parent)
        Location.__init__(self,doc,startPosition) # type: ignore
        self._html:typing.Optional[str]=None
        self._dataProvider:typing.Optional[str]\
            =None # actual data this comes from
        self._words:typing.Optional[typing.List["DocFrag"]]=None # a cache
        self._sentences:typing.Optional[typing.List["DocFrag"]]=None # a cache
        self._paragraphs:typing.Optional[typing.List["DocFrag"]]=None # a cache
        self.include:bool\
            =True # use this to skip a doc frag when compiling document
        self.title:typing.Optional[str]=None
        self.includeInFinalDocument:bool=True

    @property
    def compile(self)->bool:
        """
        whether to include this in the final document
        """
        return self.includeInFinalDocument
    @compile.setter
    def compile(self,value:bool):
        self.includeInFinalDocument=value

    @property
    def name(self)->str:
        """
        get the name of this docfrag
        """
        return self.title if self.title is not None else ''
    @name.setter
    def name(self,name:str):
        self.title=name

    def fixTitle(self)->None:
        """
        Fix the title to conform to proper grammar
        """
        from docStructure import fixTitle
        self.title=fixTitle(self.title)

    @property
    def json(self)->typing.Dict[str,typing.Any]:
        """
        get the JSON representation of this docfrag
        """
        ret:typing.Dict[str,typing.Any]={
            'frag':self.frag
        }
        if hasattr(self,'title'):
            if self.title is None:
                ret['title']=''
            else:
                ret['title']=self.title
        children:typing.List[typing.Dict[str,typing.Any]]=[
            child.json for child in self.children]
        if children:
            ret['children']=children
        return ret
    @property
    def jsonString(self)->str:
        """
        get the JSON string representation of this docfrag
        """
        from json import dumps
        return dumps(self.json)

    @property
    def root(self)->"DocFrag":
        """
        the root of the document
        """
        r=self
        while self.parent is not None and self.parent is not self: # type: ignore # noqa: E501
            r=self.parent
        return r

    @property
    def dataProvider(self)->typing.Optional["Document"]:
        """
        retrieve the data provider that generated this docfrag
        """
        if self._dataProvider is not None:
            ret=self._dataProvider
        else:
            ret=self.parent.dataProvider
            if ret is None:
                ret=self.doc
        if ret is None: # type: ignore
            raise Exception(self.__class__.__name__+' - dataProvider has gone missing!!!') # noqa: E501 # pylint: disable=line-too-long
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
            if text is None: # type: ignore
                text=''
            #elif isinstance(text,basestring):
            #    text=unicode(text,errors='replace')
        if self.position is not None: # type: ignore
            text=text[self.position[0]:self.position[1]]
        return text
    @text.setter
    def text(self,value:TextCompatible):
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
                    from htmlTools import txt2html
                    return txt2html(self.doc.txt)
                except Exception:
                    return repr(self.doc)
        elif self.text is not None:
            from htmlTools import txt2html
            return txt2html(self.text)
        return self._html
    @html.setter
    def html(self,value:HtmlCompatible):
        """
        assign the docfrag to a piece of html
        """
        if value not in [str,str]:
            value=str(value)
        if self.doc is not None:
            try:
                self.doc.html=value
            except Exception:
                from htmlTools import html2txt
                self.doc.text=html2txt(value)

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
        if self.children is not None: # type: ignore
            for c in self.children:
                c.clearCache()

    def hasChildren(self)->bool:
        """
        returns whether this item has children or not
        """
        return self.children is not None and self.children # type: ignore

    def __iter__(self)->typing.Iterator["DocFrag"]:
        # TODO: this does not work, and I don't know why I was doing it anyway
        #if not hasattr(self,'children'):
        #    print('ERR: No member "children" for '+self.__class__.__name__,dir(self)) # noqa: E501
        return iter(self.children)

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
    def count(self,
        sub:str,
        start:int=0,
        end:typing.Optional[int]=None
        )->int: # pylint: disable=arguments-differ
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
    def endswith(self,
        suffix:str,
        start:int=0,
        end:typing.Optional[int]=None
        )->bool:
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
    def format(self,
        *args:typing.ParamSpecArgs,
        **kwargs:typing.ParamSpecKwargs
        )->str:
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
    def rjust(self,width:int,fillchar:str=' '):
        """
        string method
        """
        return self.text.rjust(width,fillchar)
    def rpartition(self,sep:str):
        """
        string method
        """
        return self.text.rpartition(sep)
    def rsplit(self,sep,maxsplit=None):
        """
        string method
        """
        return self.text.rsplit(sep,maxsplit)
    def rstrip(self,chars:typing.Optional[str]=None):
        """
        string method
        """
        return self.text.rstrip(chars)
    def split(self,sep:str,maxsplit:int=-1):
        """
        string method
        """
        return self.text.split(sep,maxsplit)
    def splitlines(self,keepends:bool=False):
        """
        string method
        """
        return self.text.splitlines(keepends)
    def startswith(self,prefix:str,start:int=0,end:typing.Optional[int]=None):
        """
        string method
        """
        return self.text.startswith(prefix,start,end)
    def strip(self,chars:typing.Optional[str]=None):
        """
        string method
        """
        return self.text.strip(chars)
    def swapcase(self)->str:
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
    def translate(self, # type: ignore
        table:typing.Dict[int,str],
        deletechars:typing.Optional[str]=None):
        """
        string method
        """
        return self.text.translate(table,deletechars) # type: ignore
    def upper(self)->str:
        """
        string method
        """
        return self.text.upper()
    def zfill(self,width:int)->str:
        """
        string method
        """
        return self.text.zfill(width)
    def isnumeric(self)->bool:
        """
        string method
        """
        return self.text.isnumeric()
    def isdecimal(self)->bool:
        """
        string method
        """
        return self.text.isdecimal()
    # -------------- end string methods

    def wordAt(self,idx:int)->str:
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

    @typing.overload
    def __getitem__(self,idx:typing.Union[int,self.nodeTreeString])->'DocFrag':
        ...
    @typing.overload
    def __getitem__(self,idx:slice)->typing.Iterable['DocFrag']:
        ...
    def __getitem__(self, # type: ignore
        idx:typing.Union[int,slice,str]
        )->typing.Union['DocFrag',typing.Iterable['DocFrag']]:
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
        if not isinstance(children,list):
            children=list(children)
        if isinstance(idx,str):
            for child in children:
                if child.name==idx:
                    return child
            raise IndexError('index out of bounds!')
        return children[idx]
    def __setitem__(self, # type: ignore
        idx:typing.Union[int,str],
        val:typing.Union[str,typing.Any]):
        """
        idx can be an integer or a slice object:
            https://docs.python.org/2/c-api/slice.html
        """
        if not isinstance(val,str):
            val=str(val)
        if isinstance(idx,str):
            for child in self.children:
                if child.name==idx:
                    child.assign(val)
                    return
            raise IndexError('index out of bounds!')
        # assume int for now
        absoluteLocation=self.position[0]+idx
        for child in self.children:
            if absoluteLocation<child.position[1]:
                child[absoluteLocation-child.position[0]].assign(val)
        raise IndexError('index out of bounds!')

    def slice(self,start:int=0,end:typing.Optional[int]=None)->str:
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

    def trunc(self,s:str,pos:int=75)->str:
        """
        truncates a block of text for readability
        e.g. "four score and seven years ago [...]"
        """
        if len(s)>pos:
            return s[0:pos]+'[...]'
        return s

    def assign(self,value:str)->None:
        """
        assign the text of this item to a given value
        """
        self.set(self.location.startPosition,value)

    def findChildren(self,
        fragType:typing.Optional[str]=None,
        index:typing.Union[None,int,slice]=None
        )->typing.Iterable["DocFrag"]:
        """
        deapth-first traversal
        """
        if index is not None:
            if isinstance(index,int):
                for i,child in enumerate(self.findChildren(fragType)):
                    if i==index:
                        yield child
                        return
            else: # isinstance(index,slice)
                for i,child in enumerate(self.findChildren(fragType)):
                    if i>=index.start:
                        yield child
                        if index.stop is not None and i>=index.stop-1:
                            return
            return
        for child in self.children:
            if fragType is None or fragType==child.frag:
                yield child
            yield from child.findChildren(fragType)
    def findParent(self,
        fragType:typing.Optional[str]=None
        )->typing.Optional["DocFrag"]:
        """
        find the nearest parent of the specified fragment type
        """
        if self.parent is None:
            return None
        if fragType is None or self.parent.frag==fragType:
            return self.parent
        return self.parent.findParent(fragType)

    @property
    def words(self)->typing.Iterator["Word"]:
        """
        get all words within this doc frag
        """
        return self.findChildren('word') # type: ignore
    @property
    def chapters(self)->typing.Iterable["Chapter"]:
        """
        get all chapters within this doc frag
        """
        return self.findChildren('chapter') # type: ignore
    @property
    def paragraphs(self)->typing.Iterable["Paragraph"]:
        """
        get all paragraphs within this doc frag
        """
        return self.findChildren('paragraph') # type: ignore
    @property
    def sentences(self)->typing.Iterable["Sentence"]:
        """
        get all sentences within this doc frag
        """
        return self.findChildren('sentence') # type: ignore
    @property
    def sections(self)->typing.Iterable["Section"]:
        """
        get all sections within this doc frag
        """
        return self.findChildren('section') # type: ignore
    @property
    def comments(self)->typing.Iterable["Comment"]:
        """
        get all comments within this doc frag
        """
        return self.findChildren('comment') # type: ignore

    def getWords(self,
        index:typing.Union[None,int,slice]=None
        )->typing.Iterator["Word"]:
        """
        get the words within this doc frag, optionally specifying a range
        """
        return self.findChildren('word',index) # type: ignore
    def getWord(self,index:int)->"Word":
        """
        get a single word by its index within this doc frag
        """
        for word in self.getWords(index):
            return word
        raise IndexError("Word index out of range")
    def getChapters(self,
        index:typing.Union[None,int,slice]=None
        )->typing.Iterable["Chapter"]:
        """
        get the chapters within this doc frag, optionally specifying a range
        """
        return self.findChildren('chapter',index) # type: ignore
    def getChapter(self,index:int)->"Chapter":
        """
        get a single chapter by its index within this doc frag
        """
        for chapter in self.getChapters(index):
            return chapter
        raise IndexError("Chapter index out of range")
    def getParagraphs(self,
        index:typing.Union[None,int,slice]=None
        )->typing.Iterable["Paragraph"]:
        """
        get the paragraphs within this doc frag, optionally specifying a range
        """
        return self.findChildren('paragraph',index) # type: ignore
    def getParagraph(self,index:int)->"Paragraph":
        """
        get a single paragraph by its index within this doc frag
        """
        for paragraph in self.getParagraphs(index):
            return paragraph
        raise IndexError("Paragraph index out of range")
    def getSentences(self,
        index:typing.Union[None,int,slice]=None
        )->typing.Iterable["Sentence"]:
        """
        get the sentences within this doc frag, optionally specifying a range
        """
        return self.findChildren('sentence',index) # type: ignore
    def getSentence(self,index:int)->"Sentence":
        """
        get a single sentence by its index within this doc frag
        """
        for sentence in self.getSentences(index):
            return sentence
        raise IndexError("Sentence index out of range")
    def getSections(self,
        index:typing.Union[None,int,slice]=None
        )->typing.Iterable["Section"]:
        """
        get the sections within this doc frag, optionally specifying a range
        """
        return self.findChildren('section',index) # type: ignore
    def getSection(self,index:int)->"Section":
        """
        get a single section by its index within this doc frag
        """
        for section in self.getSections(index):
            return section
        raise IndexError("Section index out of range")
    def getComments(self,
        index:typing.Union[None,int,slice]=None
        )->typing.Iterable["Comment"]:
        """
        get the comments within this doc frag, optionally specifying a range
        """
        return self.findChildren('comment',index) # type: ignore
    def getComment(self,index:int)->"Comment":
        """
        get a single comment by its index within this doc frag
        """
        for comment in self.getComments(index):
            return comment
        raise IndexError("Comment index out of range")

    @property
    def wordCount(self)->int:
        """
        how many words are associated with this doc frag
        """
        return len(list(self.words))
    numWords=wordCount
    @property
    def sentenceCount(self)->int:
        """
        how many sentences are associated with this doc frag
        """
        return len(list(self.sentences))
    numSentences=sentenceCount
    @property
    def paragraphCount(self)->int:
        """
        how many paragraphs are associated with this doc frag
        """
        return len(list(self.paragraphs))
    numParagraphs=paragraphCount
    @property
    def chapterCount(self)->int:
        """
        how many chapters are associated with this doc frag
        """
        return len(list(self.chapters))
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
        ret:typing.List[str]=[]
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
            ret.append('In '+hl[0]) # include it anyway so we have something to show # noqa: E501
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
            self.chapterNum,
            self.paragraphNum,
            self.sentenceNum,
            self.wordNum)


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
        return -1
    return 0


if __name__=='__main__':
    import sys
    sys.exit(cmdline(sys.argv[1:]))
