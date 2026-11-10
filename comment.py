#!/usr/bin/env
# -*- coding: utf-8 -*-
"""
This class represents a comment.

This inserts a logical level between Chapter and Paragraph items.

NOTE: Its contents are outside of the document flow so comment.words will neither
show up in comment.chapter.words,nor will it increase word count.
"""
import typing
import nltk
from docStructure import DocFrag,findTokenLocations,Location
if typing.TYPE_CHECKING:
    from docStructure import  Sentence


class Comment(DocFrag):
    """
    This class represents a comment.

    This inserts a logical level between Chapter and Paragraph items.

    NOTE: Its contents are outside of the document flow so comment.words will neither
    show up in comment.chapter.words,nor will it increase word count.
    """

    def __init__(self,doc,parent:DocFrag,position:int):
        """
        :param doc: the document this paragraph belongs to
        :param parent: the parent object in the hierarchy
        :param position: the actual location of this item
        """
        DocFrag.__init__(self,doc,parent,position)
        self._sentenceCount=None
        self.location=position
        self.children=[]

    def set(self,location:Location,text:str)->None: # pylint: disable=arguments-differ
        """
        Assign this comment to the given text.

        Will automatically update child items (sentences and words).

        :param location: set where this item is in the document
        :param text: set the text value
        """
        self.location=location
        self.children=[]
        sentences=nltk.sent_tokenize(text)
        locations=findTokenLocations(text,sentences,self.location[0])
        for i,sentence in enumerate(sentences):
            sent=Sentence(self.doc,self,locations[i])
            sent.set(locations[i],sentence)
            self.children.append(sent)

    def paragraphNum(self):
        """
        para number within chapter

        TODO: does this make sense?
        """
        return self.parent.paragraphs.index(self)

    def chapterNum(self):
        """
        chapter number within document
        """
        return self.parent.chapterNum()

    @property
    def words(self):
        """
        get all words within this comment.

        NOTE: these are outside of the document flow and therefore
            will NOT show up in self.chapter.words!

            Nor will these words increase the document word count.
        """
        if self._words is None:
            self._words=[]
            for s in self.sentences:
                self._words.extend(s.words)
        return self._words

    @property
    def sentences(self):
        """
        Get all sentences  within this comment.

        NOTE: these are outside of the document flow and therefore
            will NOT show up in self.chapter.sentences!
        """
        if self._sentences is None:
            self._sentences=[]
            for p in self.paragraphs:
                self._sentences.extend(p.sentences)
        return self._sentences

    @property
    def paragraphs(self):
        """
        Get all paragraphs within this comment.

        NOTE: these are outside of the document flow and therefore
            will NOT show up in self.chapter.paragraphs!
        """
        return self.children

    @property
    def chapters(self):
        """
        get all chapters related to this frag

        In a practical sense,this will be [theParentChapter]
        """
        return [self.parent]


def cmdline(args):
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
