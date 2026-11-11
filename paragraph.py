#!/usr/bin/env
# -*- coding: utf-8 -*-
"""
This class represents a single paragraph
"""
import typing
from docStructure import DocFrag,findTokenLocations
if typing.TYPE_CHECKING:
    from docStructure import Sentence,Document


class Paragraph(DocFrag):
    """
    This class represents a single paragraph
    """

    frag='paragraph'

    def __init__(self,doc:"Document",parent:DocFrag,startPosition:int=0):
        """
        :param doc: the document this paragraph belongs to
        :param parent: the parent object in the hierarchy
        :param startPosition: the actual location of this item
        """
        DocFrag.__init__(self,doc,parent,startPosition)
        self._sentenceCount=None

    def set(self, # type: ignore
        startPosition:int,
        text:str
        )->None:
        """
        Assign this paragraph to the given text.

        Will automatically update child items (sentences and words).

        :param position: set where this item is in the document
        :param text: set the text value
        """
        self.position=position
        self.children:typing.List["Sentence"]=[]
        try:
            import nltk # type: ignore
            sentences=nltk.sent_tokenize(text) # type: ignore
        except ImportError:
            raise ImportError("NLTK is required for sentence tokenization")
        sentences=typing.cast(typing.List[str],sentences)
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
                kv=[a.strip() for a in arg.split('=',1)]
                if kv[0] in ('-h','--help'):
                    printhelp=True
                else:
                    print('ERR: unknown argument "'+kv[0]+'"')
            else:
                print('ERR: unknown argument "'+arg+'"')
    if printhelp:
        print('Usage:')
        print('  Paragraph.py [options]')
        print('Options:')
        print('   NONE')
        return -1
    return 0


if __name__=='__main__':
    import sys
    sys.exit(cmdline(sys.argv[1:]))
