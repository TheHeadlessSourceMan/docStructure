#!/usr/bin/env
# -*- coding: utf-8 -*-
"""
This class represents a single character.  Most of the time
the smartest thing is to simply use a character,unless you have a situation where
a single character occupies multiple characters in the document,for instance,&gt;
"""
from .docFrag import DocFrag


class Character(DocFrag):
    """
    This class represents a single character.  Most of the time
    the smartest thing is to simply use a character,unless you have a situation where
    a single character occupies multiple characters in the document,for instance,&gt;
    """

    def __init__(self,doc,parent:DocFrag,position:int):
        """
        :param doc: the document this paragraph belongs to
        :param parent: the parent object in the hierarchy
        :param position: the actual location of this item
        """
        DocFrag.__init__(self,doc,parent,position)
        self.actual=None # actual character representation (a str or unicode)

    def wordNum(self):
        """
        word number within sentence
        """
        return self.parent.wordNum()

    def sentenceNum(self):
        """
        sentence number within paragraph
        """
        return self.parent.parent.sentenceNum()

    def paragraphNum(self):
        """
        para number within chapter
        """
        return self.parent.parent.parent.paragraphNum()

    def chapterNum(self):
        """
        chapter number within document
        """
        return self.parent.parent.parent.parent.chapterNum()

    def __str__(self)->str:
        return self.actual


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
        print('  Character.py [options]')
        print('Options:')
        print('   NONE')


if __name__=='__main__':
    import sys
    cmdline(sys.argv[1:])