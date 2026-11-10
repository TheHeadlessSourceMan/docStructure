#!/usr/bin/env
# -*- coding: utf-8 -*-
"""
This class represents a single sentence
"""
import typing
import nltk
from docStructure import findTokenLocations, DocFrag
if typing.TYPE_CHECKING:
    from docStructure import Word, Document


class Sentence(DocFrag):
    """
    This class represents a single sentence
    """

    frag='sentence'

    def __init__(self,doc:"Document",parent:DocFrag,position:int=0):#(self,value,doc=None,line=0,position=0):
        """
        :param doc: the document this paragraph belongs to
        :param parent: the parent object in the hierarchy
        :param position: the actual location of this item
        """
        #location.__init__(self,doc,line,position)
        #self.__eq__(value)
        #self.words=' '.split(value)
        #for i in range(self.words):
        #    self.words[i]=Word(self.words[i],doc,line,position)
        #    position=position+len(word)+1 # TODO: This could be better
        DocFrag.__init__(self,doc,parent,position)
        self.location=position
        self.children=[]

    def set(self,location:int,text:str)->None:
        """
        Assign this sentence to the given text.

        Will automatically update child items (aka,words).

        :param location: set where this item is in the document
        :param text: set the text value
        """
        self.location=location
        self.children=[]
        # TODO: this tokenizer does not work well.
        #    see: https://github.com/armatthews/TokenizeAnything
        words=nltk.word_tokenize(text)
        locs=findTokenLocations(text,words,self.location[0])
        # TODO: this tokenizer doesn't work well either
        # looking into BLLIP,but this bug:
        #    https://github.com/BLLIP/bllip-parser/issues/48
        partsOfSpeech=nltk.pos_tag(words) # where tokens is [(word,part_of_speech)]
        for i,p in enumerate(partsOfSpeech):
            w=Word(self.doc,self,locs[1])
            w.set(locs[i],p[0],p[1])
            self.children.append(w)

    def replace(self,old:str,new:str,count:typing.Optional[int]=None)->str:
        raise NotImplementedError()

    def sentenceNum(self)->int:
        """
        sentence number within paragraph
        """
        return self.parent.sentences.index(self)

    def paragraphNum(self)->int:
        """
        para number within chapter
        """
        return self.parent.paragraphNum()

    def chapterNum(self)->int:
        """
        chapter number within document
        """
        return self.parent.parent.chapterNum()

    def structure(self)->str:
        """
        :return: the grammatical structure of this sentence
        """
        if True:
            rd_parser=nltk.RecursiveDescentParser(nltk.grammar)
            for tree in rd_parser.parse([w.word for w in self.children]):
                print(tree)
        else:
            from nltk.data import find
            model_dir=find('models/bllip_wsj_no_aux').path
            print('Loading BLLIP Parsing models...')
            from bllipparser import BllipParser
            bllip=BllipParser(model_dir)
            print('Done.')
            tree=bllip.parse_one([w.word for w in self.children])
            print(tree)

    @property
    def words(self)->typing.Iterable["Word"]:
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
                if arg in ['-h','--help']:
                    printhelp=True
                else:
                    print('ERR: unknown argument "'+arg+'"')
            else:
                print('ERR: unknown argument "'+arg+'"')
    if printhelp:
        print('Usage:')
        print('  Sentence.py [options]')
        print('Options:')
        print('   NONE')


if __name__=='__main__':
    import sys
    cmdline(sys.argv[1:])