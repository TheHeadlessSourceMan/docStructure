#!/usr/bin/env
# -*- coding: utf-8 -*-
"""
This class represents a single word
"""
import typing
from docStructure import DocFrag, Document


class WordInfo:
    """
    Information about a word (such as definition,etc)
    """

    frag='word'

    def __init__(self):
        self.locations:typing.List[int]=[]
        self._definitions:typing.Optional[typing.List[str]]=None

    # TODO: not sure what I was going for with assign(), but it appears to be incomplete
    # def assign(self,value:str)->None:
    #     """
    #     assign to a particular value

    #     NOTE: this can raise an execption when trying to assign a multi-word string
    #     """
    #     from . import htmlDocument
    #     if not isinstance(value,htmlDocument.HtmlDocument):
    #         value=htmlDocument.HtmlDocument(data=str(value))
    #     if value.numWords>1:
    #         raise Exception('ERR: cannot assign multiple words to a single word object')
    #     if value.numWords==1:
    #         word=value.words[0]
    #     else:
    #         word=''

    def wordName(self)->str:
        """
        the name of this word
        """
        return self.locations[0].value()

    def proximities(self)->int:
        """
        gets how near every instance of a word is to itsself

        :return: (space_between,instance1,instance2)
        """
        for i in range(len(self.locations)-1):
            for j in range(i+1):
                if self.locations[i].valueStart !=self.locations[j].valueStart:
                    space_between=self.locations[i].valueEnd-self.locations[j].valueStart
                    yield (space_between,self.locations[i],self.locations[j])

    def closestProximity(self)->int:
        """
        like proximities(),but only returns the closest two words

        :return: (space_between,instance1,instance2)
                    can return None if there is one occurrence
        """
        proximities=[x for x in self.proximities()]
        if not proximities:
            return None
        proximities.sort(key=lambda t: t[0])
        return proximities[0]
        #return sorted(self.proximities(),key=lambda t: t[0])[0]

    def getDefinitions(self)->typing.Iterable[str]:
        """
        Get associated definition(s) for this word
        """
        if self._definitions is None:
            import Dictionary
            self._definitions=Dictionary.getDefinitions(self.wordName)
        return self._definitions

    def __repr__(self)->str:
        """
        text representation of this word
        """
        return self.wordName()


class Word(DocFrag):
    """
    This class represents a single word
    """

    _globalReferenceDictionary=None # there will be only one instance

    def __init__(self,doc:Document,parent:DocFrag,position:int):#,value,doc=None,line=0,position=0):
        """
        :param doc: the document this paragraph belongs to
        :param parent: the parent object in the hierarchy
        :param position: the actual location of this item
        """
        DocFrag.__init__(self,doc,parent,position)
        #self.__eq__(value)
        self._syllables=None
        self.partOfSpeech=None

    @property
    def json(self):
        ret=super().json
        ret['data']=self.text
        return ret

    def set(self,location:int,text:str,partOfSpeech:str)->None:
        """
        :param location: set where this item is in the document
        :param text: set the text value
        :param partOfSpeech: what part of speech this word is
        """
        self.location=location
        self.partOfSpeech=partOfSpeech

    def getRoot(self)->str:
        """
        Get the root/stem of this word.
        """
        self.doc._wordRoot(str(self))

    def wordNum(self)->int:
        """
        word number within sentence
        """
        return self.parent.words.index(self)

    def sentenceNum(self)->int:
        """
        sentence number within paragraph
        """
        return self.parent.sentenceNum()

    def paragraphNum(self)->int:
        """
        para number within chapter
        """
        return self.parent.parent.paragraphNum()

    def chapterNum(self)->int:
        """
        chapter number within document
        """
        return self.parent.parent.parent.chapterNum()

    @property
    def referenceDictonary(self)->typing.Dict[str,str]:
        """
        :return: the reference dictionary -- will be automatically loaded as necessary
        """
        if self.__class__._globalReferenceDictionary is None:
            print('Loading dictionary...')
            #import nltk
            from nltk.corpus import cmudict
            self.__class__._globalReferenceDictionary=cmudict.dict()
        return self.__class__._globalReferenceDictionary

    @property
    def definition(self)->str:
        """
        :return: the (first) definition for this word
        """
        return self.referenceDictonary[str(self).lower()]

    @property
    def syllables(self)->int:
        """
        :return: the number of syllables (useful when doing poetry)
        """
        if self._syllables is None:
            text=str(self).lower().strip()
            if not text or not text[0].isalpha():
                self._syllables=0
            else:
                try:
                    self._syllables=[len(list(y for y in x if y[-1].isdigit())) for x in self.referenceDictonary[text]][0]
                except KeyError:
                    w=text.encode(sys.stdout.encoding,errors='replace')
                    print('WARN: Unable to find definition for "'+w+'"')
                    print('      '+self.descriptiveLocation(False))
                    self._syllables=0
        return self._syllables


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
                if arg in ['-h','--help']:
                    printhelp=True
                else:
                    print('ERR: unknown argument "'+arg+'"')
            else:
                print('ERR: unknown argument "'+arg+'"')
    if printhelp:
        print('Usage:')
        print('  Word.py [options]')
        print('Options:')
        print('   NONE')


if __name__=='__main__':
    import sys
    cmdline(sys.argv[1:])
