#!/usr/bin/env
# -*- coding: utf-8 -*-
"""
This class represents a single paragraph
"""
import typing
import nltk
from docStructure import DocFrag, findTokenLocations
if typing.TYPE_CHECKING:
    from docStructure import Sentence, Document


class Paragraph(DocFrag):
    """
    This class represents a single paragraph
    """

    frag='paragraph'

    def __init__(self,doc:"Document",parent:DocFrag,position:int):
        """
        :param doc: the document this paragraph belongs to
        :param parent: the parent object in the hierarchy
        :param position: the actual location of this item
        """
        DocFrag.__init__(self,doc,parent,position)
        self._sentenceCount=None

    def set(self,position:int,text:str)->None:
        """
        Assign this paragraph to the given text.

        Will automatically update child items (sentences and words).

        :param position: set where this item is in the document
        :param text: set the text value
        """
        self.position=position
        self.children=[]
        sentences=nltk.sent_tokenize(text)
        locations=findTokenLocations(text,sentences,self.location[0])
        for i,sentence in enumerate(sentences):
            sent=Sentence(self.doc,self,locations[i])
            sent.set(locations[i],sentence)
            self.children.append(sent)

    def paragraphNum(self)->int:
        """
        para number within chapter
        """
        return self.parent.paragraphs.index(self)

    def chapterNum(self)->int:
        """
        chapter number within document
        """
        return self.parent.chapterNum()

    @property
    def sentences(self)->typing.Iterable["Sentence"]:
        """
        get all sentences related to this frag
        (be it a parent sentence or child sentences)
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
        print('  Paragraph.py [options]')
        print('Options:')
        print('   NONE')


if __name__=='__main__':
    import sys
    cmdline(sys.argv[1:])