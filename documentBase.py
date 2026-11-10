#!/usr/bin/env
# -*- coding: utf-8 -*-
"""
This is a generic base document that is derived by whatever file type you want.

NOTE: there is also a generic MultiFileDocument,which should be used instead if the
type in question contains many sub-documents
"""
import typing
from paths import MimeType, URL
from docStructure import Section, DocFrag
if typing.TYPE_CHECKING:
    from docStructure import WordInfo, Word, Chapter


class DocumentBase(Section):
    """
    This is a generic base document that is derived by whatever file type you want.

    NOTE: there is also a generic MultiFileDocument,which should be used instead if the
    type in question contains many sub-documents
    """

    _LEMMATIZER=None

    #def __new__(cls,parent=None):
    #    obj=DocFrag.__new__(cls,parent,None,(0,0))
    #    return obj

    frag='book'

    def __init__(self,parent:typing.Optional["DocumentBase"]=None):
        if parent is None:
            parent=self
        Section.__init__(self,self,parent,0)
        self._delegateDocument:typing.Optional[DocumentBase]=None
        self._linesLen:typing.Optional[int]=None
        self.mimeType:typing.Optional[MimeType]=None
        self.name:typing.Optional[str]=None
        self.location:typing.Optional[URL]=None
        self.title:str=''
        self._wordInfo:typing.Optional["WordInfo"]=None # {word:WordInfo}\
        self.dirty:bool=False # track whether or not the document has changed
        self._infoByCategory:typing.Dict[str,"WordInfo"]={}

    def fixTitle(self)->str:
        """
        Fix the title to conform to proper grammar
        """
        from docStructure import fixTitle
        self.title=fixTitle(self.title)

    #@property
    #def title(self):
    #    raise NotImplementedError(self.__class__.__name__+'.title')

    def _wordRoot(self,text:str)->str:
        """
        get the undecorated version of a word:
            cat=> cat
            cats=> cat
            run=> run
            ran=> run
            running=> run
        see:
            http://www.nltk.org/api/nltk.stem.html
        """
        if self._LEMMATIZER is None:
            from nltk.stem import WordNetLemmatizer
            self._LEMMATIZER=WordNetLemmatizer()
        return self._LEMMATIZER.lemmatize(text)

    def assign(self,value:str)->None:
        """
        :param value: can be
            * anything derived from DocumentBase
            * anything that can create an HtmlDocument
        """
        from docStructure import HtmlDocument
        if not isinstance(value,DocumentBase):
            #raise(str(type(value)))
            value=HtmlDocument(value)
        self.html=value.html
        self._infoByCategory=value._infoByCategory.copy()

    def set(self,text:str,name:str='[untitled]')->None: # pylint: disable=arguments-differ
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
                import urllib.request
                import urllib.error
                import urllib.parse
                location=[urllib.request.url2pathname(location[1])]
            if len(location)>1:
                import urllib.request
                import urllib.error
                import urllib.parse
                f=urllib.request.urlopen(self.location)
                text=f.read()
                f.close()
                text=str(text,errors='replace')
            else:
                f=open(location[0],'rb')
                text=f.read().decode('utf-8',errors="ignore")
                f.close()
                text=str(text,errors='replace')
        self.name=name
        self.text=text

    @property
    def children(self)->typing.Iterator["Chapter"]:
        """
        :return: the immediate children of this object
        """
        if self._delegateDocument is not None:
            return self._delegateDocument.children
        ret=[]
        #for c in nltk.chap_tokenize(doc):
        #    c=Chapter(c)
        #    ret.append(c)
        c=Chapter(self,self,(0,0))
        c.set(self.location,self.text)
        ret.append(c)
        return ret

    def offsToLine(self,location:int,zeroBased:bool=False)->int:
        """
        Converts a character location into (line,char_offset).  This is useful
        when highlighting errors in a user interface.

        :param location: a character position offset within the file
        :param zeroBased: if True,the first character is (0,0) otherwise it is (1,1)

        :return: the document offset
        """
        if self._delegateDocument is not None:
            return self._delegateDocument.offsToLine(location,zeroBased)
        if self._linesLen is None:
            self._linesLen=[]
            i=0
            for line in self.text.split('\n'):
                i=i+len(line)+1
                #print('line end pos=',i)
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

    def uniqueWordCount(self)->int:
        """
        :return: how many words are unique within the document

        TODO: there are more useful ways to get this metric
        """
        return len(list(self.getWordInfo().values()))

    def getWordInfo(self)->"WordInfo":
        """
        :return: a WordInfo object for every word in the document
        """
        if self._wordInfo is None:
            self._wordInfo={}
            for word in self.words:
                wordText=word.value()
                if wordText not in self._wordInfo:
                    from docStructure import WordInfo
                    self._wordInfo[wordText]=WordInfo()
                self._wordInfo[wordText].locations.append(word)
        return self._wordInfo

    def getWordUsage(self)->typing.List[typing.Tuple[int,"Word"]]:
        """
        Gets the number of occurrences of every word in the document.  This is useful
        when detecting which words the author tends to over-use.

        :return: [(count,word)] for every word in the tree in order from greatest to least
        """
        allwords=self.getWordInfo()
        results=[(len(w.locations),w) for w in list(allwords.values())]
        results.sort(key=lambda t: t[0],reverse=True)
        return results

    def closestProximityOfWords(self)->typing.Tuple[int,"Word","Word"]:
        """
        Gets the closes proximity of each word to itself.

        :return: (space_between,instance1,instance2)
        """
        results=[]
        for w in list(self.getWordInfo().values()):
            prox=w.closestProximity()
            if prox is not None:
                results.append(prox)
        results.sort(key=lambda t: t[0])
        return results

    @property
    def chapterNames(self)->typing.Iterable[str]:
        """
        The names (in order) of all of the chapters
        """
        return [x.name for x in self.chapters]

    def removeChapter(self,chapter:"Chapter")->None:
        """
        remove a chapter

        :param startChapter: can be a number,a Chapter object,or a chapter title
        """
        if not isinstance(chapter,Chapter):
            if isinstance(chapter,(int,float)):
                i=int(chapter)
            else:
                i=self.chapterNames.index(chapter)
        else:
            i=self.chapters.index(chapter)
        # now go get it
        ii=[0] # in a list to prevent scoping issues
        def q(parent):
            for iii,ch in enumerate(parent):
                if isinstance(ch,Chapter):
                    ii[0]+=1
                    if i==ii[0]:
                        del ch.children[iii]
                        return
                    q(ch)
        q(self)

    def cropToChapters(self,
        startChapter:typing.Union[None,"Chapter",str]=None,
        endChapter:typing.Union[None,"Chapter",str]=None
        )->None:
        """
        crop the document to just the given chapters

        :param startChapter: can be None,a Chapter object,or a chapter title
        :param endChapter: can be None,a Chapter object,or a chapter title
        """
        keep=[]
        inRange=False
        for ch in self.chapters:
            if startChapter is None or ch==startChapter:
                inRange=True
            if inRange:
                if not isinstance(ch.parent,Chapter) or ch.parent not in keep:
                    keep.append(ch)
                if ch is not None and ch==endChapter:
                    inRange=False
                    break
        self.children=keep

    @property
    def dataProvider(self)->"DocumentBase":
        """
        :return: the item responsible for providing this doc
        """
        return self._dataProvider

    @property
    def categoryNames(self)->typing.Iterable[str]:
        """
        returns available category names
        """
        return list(self._infoByCategory.keys())

    def _loadInfo(self,category:str)->typing.List:
        """
        load the database info for a given category

        :return: [infoObj]

        NOTE: not all documents support this, for instance
            if it's simply a libreoffice document or html file
        """
        return []

    def getInfo(self,
        category:typing.Optional[str]=None
        )->typing.Union[typing.List[DocFrag],typing.Dict[str,typing.List[DocFrag]]]:
        """
        Get all db items in a given category

        :param category: can be 'location','character'
            if None,get all as a {category:[items]}

        :return: [] of items or {category:[items]}
        """
        ret=[]
        if category is not None:
            if category not in self._infoByCategory:
                self._infoByCategory[category]=self._loadInfo(category)
            ret=self._infoByCategory[category]
        else:
            ret={}
            for k in self.categoryNames:
                ret[k]=self.getInfo(category)
        return ret

    def clearInfo(self,category:typing.Optional[str]=None)->None:
        """
        Clear all db items in a given category

        :param category: can be 'location','character'
            if None,clear all categories
        """
        if category is None:
            self._infoByCategory={}
        else:
            del self._infoByCategory[category]

    def addInfo(self,item:DocFrag,category:str)->None:
        """
        Add an item to the given category

        :param item: any valid item object(s) for this database
            * can be a list of items
            * If it's a DocumentBase,then all items will be added (category is unused)
        :param category: can be 'location','character'
        """
        if isinstance(item,DocumentBase):
            for k,v in list(item.getInfo().items()):
                self.addInfo(v,k)
        elif hasattr(item,'__iter__'):
            for itemChild in item:
                self.addInfo(itemChild,category)
        else:
            if category not in self._infoByCategory:
                self._infoByCategory[category]=[item]
            else:
                self._infoByCategory[category].append(item)


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
                arg[0]=arg[0].lower()
                if arg in ['-h','--help']:
                    printhelp=True
                else:
                    print('ERR: unknown argument "'+arg[0]+'"')
            else:
                print('ERR: unknown argument "'+arg+'"')
    if printhelp:
        print('Usage:')
        print('  DocumentBase.py file [commands]')
        print('Commands:')
        print('  [none]')


if __name__=='__main__':
    import sys
    cmdline(sys.argv[1:])