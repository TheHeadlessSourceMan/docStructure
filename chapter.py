#!/usr/bin/env
# -*- coding: utf-8 -*-
"""
This class represents a single chapter
"""
import typing
import re
from docStructure import DocFrag
if typing.TYPE_CHECKING:
    from .word import Word
    from .sentence import Sentence
    from .paragraph import Paragraph
    from .section import Section
    from .document import Document


class Chapter(DocFrag):
    """
    This class represents a single chapter

    NOTE: chapter demarcations are defined by two or more consecutive newlines
    """

    frag='chapter'
    _SPLITTER=re.compile(
        r"""(?:\s*)(.+?)(?:(?:\s*\Z)|(?:\s*?\n(?:\s*\n)+))""",
        re.DOTALL)

    def __init__(self,doc:Document,parent:DocFrag,position:int):
        """
        :param doc: the document this paragraph belongs to
        :param parent: the parent object in the hierarchy
        :param position: the actual location of this item
        """
        DocFrag.__init__(self,doc,parent,position)
        self.children:typing.List[typing.Union["Section","Paragraph"]]=[]
        self._words=None
        self._sentences=None
        self._comments=None
        self._description=None

    def set(self, # type: ignore
        startPosition:int,
        text:str,
        title:typing.Optional[str]=None):
        """
        Assign this chapter to the given text.

        Will automatically update child items (sentences and words).

        :param startPosition: set where this item is in the document
        :param text: set the text value
        :param title: the title of the chapter
        """
        from .paragraph import Paragraph
        self.children=[]
        self._comments=[]
        if title is None:
            title=''
        self.title=title
        for paragraphText in self._SPLITTER.finditer(text):
            position=(
                self.position[0]+paragraphText.start(1),
                self.position[0]+paragraphText.end(1))
            p=Paragraph(self.doc,self,position)
            p.set(self.position[0]+paragraphText.start(1),
                paragraphText.group(1))
            self.children.append(p)
        print('paragraphs=',len(self.children))

    @property
    def chapterNum(self)->int:
        """
        chapter number within document
        """
        return self.parent.chapters.index(self)

    @property
    def words(
        self)->typing.Iterable["Word"]:
        """
        get all words related to this frag
        """
        if self._words is None:
            self._words=[]
            for p in self.paragraphs:
                self._words.extend(p.words)
        return self._words

    @property
    def sentences(self)->typing.Iterable["Sentence"]:
        """
        get all sentences related to this frag
        (be it a parent sentence or child sentences)
        """
        if self._sentences is None:
            self._sentences=[]
            for p in self.paragraphs:
                self._sentences.extend(p.sentences)
        return self._sentences

    @property
    def paragraphs(self)->typing.Iterable["Paragraph"]:
        """
        get all sentences related to this frag
        (be it a parent paragraph or child paragraphs)
        """
        return self.children

    @property
    def comments(self)->typing.Iterable[str]:
        """
        get all comments within this chapter

        NOTE: every overall comment without a specific location will
            show up at the starting location of the chapter
        """
        if self._comments is None:
            return []
        return self._comments
    @comments.setter
    def comments(self,comments:typing.Iterable[str]):
        self._comments=list(comments)

    @property
    def description(self):
        """
        get the chapter description
        """
        return self._description

    @property
    def chapters(self):
        """
        get all chapters related to this frag
        (be it a parent paragraph or child chapters)
        """
        return [self]

    def __eq__(self,val:typing.Any):
        """
        Extend comparison operator so we can also compare
        against a chapter title string
        """
        if isinstance(val,int):
            return val==self.chapterNum
        if isinstance(val,str):
            return val==self.title
        return val is self


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
                kv=[a.strip() for a in arg.split('=',1)]
                if kv[0] in ('-h','--help'):
                    printhelp=True
                else:
                    print('ERR: unknown argument "'+kv[0]+'"')
            else:
                print('ERR: unknown argument "'+arg+'"')
    if printhelp:
        print('Usage:')
        print('  Chapter.py [options]')
        print('Options:')
        print('   NONE')
        return -1
    return 0


if __name__=='__main__':
    import sys
    sys.exit(cmdline(sys.argv[1:]))
