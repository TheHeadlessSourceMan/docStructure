#!/usr/bin/env
# -*- coding: utf-8 -*-
"""
This class represents a single sentence
"""
import typing
from docStructure import findTokenLocations,DocFrag
from .wordUtils import sentenceStructure, wordTokenize, wordsToPartsOfSpeech
if typing.TYPE_CHECKING:
    from .word import Word
    from .document import Document


class Sentence(DocFrag):
    """
    This class represents a single sentence
    """

    frag='sentence'

    def __init__(self,
        doc:"Document",
        parent:DocFrag,
        startPosition:int=0):
        """
        :param doc: the document this paragraph belongs to
        :param parent: the parent object in the hierarchy
        :param startPosition: the actual location of this item
        """
        #location.__init__(self,doc,line,position)
        #self.__eq__(value)
        #self.words=' '.split(value)
        #for i in range(self.words):
        #    self.words[i]=Word(self.words[i],doc,line,position)
        #    position=position+len(word)+1 # TODO: This could be better
        DocFrag.__init__(self,doc,parent,startPosition)
        self.children:typing.List["Word"]=[]

    def set(self,startPosition:int,text:str)->None:
        """
        Assign this sentence to the given text.

        Will automatically update child items (aka,words).

        :param startPosition: set where this sentence starts in the document
        :param text: set the text value
        """
        self.location.startPosition=startPosition
        self.children=[]
        words=wordTokenize(text)
        locs=findTokenLocations(text,words,self.location.startPosition)
        partsOfSpeech=wordsToPartsOfSpeech(words) # noqa: E501
        from .word import Word
        for i,p in enumerate(partsOfSpeech):
            w=Word(self.doc,self,locs[i])
            w.set(locs[i],p[0],p[1])
            self.children.append(w)

    def replace(self,old:str,new:str,count:typing.Optional[int]=None)->str:
        raise NotImplementedError()

    def sentenceNum(self)->int:
        """
        sentence number within paragraph
        """
        if self.parent is None:
            return -1
        parentSentences=list(self.parent.sentences)
        parentSentences=typing.cast(typing.List["Sentence"],parentSentences)
        return parentSentences.index(self)

    def paragraphNum(self)->int:
        """
        para number within chapter
        """
        if self.parent is None:
            return -1
        return self.parent.paragraphNum()

    def chapterNum(self)->int:
        """
        chapter number within document
        """
        if self.parent is None or self.parent.parent is None:
            return -1
        return self.parent.parent.chapterNum()

    def structure(self)->str:
        """
        :return: the grammatical structure of this sentence
        """
        return sentenceStructure(str(self))
    @property
    def words(self # type: ignore
        )->typing.Iterable["Word"]:
        """
        get all words related to this frag
        """
        return self.children


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
                else:
                    print('ERR: unknown argument "'+arg[0]+'"')
            else:
                print('ERR: unknown argument "'+arg+'"')
    if printhelp:
        print('Usage:')
        print('  Sentence.py [options]')
        print('Options:')
        print('   NONE')
        return -1
    return 0


if __name__=='__main__':
    import sys
    sys.exit(cmdline(sys.argv[1:]))
