#!/usr/bin/env
# -*- coding: utf-8 -*-
"""
This class represents a single character.  Most of the time
the smartest thing is to simply use a character,unless you have a situation
where a single character occupies multiple characters in the document, 
for instance,&gt;
"""
import typing
from .docFrag import DocFrag
if typing.TYPE_CHECKING:
    from .document import Document


class Character(DocFrag):
    """
    This class represents a single character.  Most of the time
    the smartest thing is to simply use a character,unless you have a
    situation where a single character occupies multiple characters
    in the document,for instance, &gt;
    """

    def __init__(self,doc:"Document",parent:DocFrag,position:int):
        """
        :param doc: the document this paragraph belongs to
        :param parent: the parent object in the hierarchy
        :param position: the actual location of this item
        """
        DocFrag.__init__(self,doc,parent,position)
        self.actual=None # actual character representation (a str or unicode)

    def wordNum(self)->int:
        """
        word number within sentence
        """
        return self.parent.wordNum()

    def sentenceNum(self)->int:
        """
        sentence number within paragraph
        """
        return self.parent.parent.sentenceNum()

    def paragraphNum(self)->int:
        """
        para number within chapter
        """
        return self.parent.parent.parent.paragraphNum()

    def chapterNum(self)->int:
        """
        chapter number within document
        """
        return self.parent.parent.parent.parent.chapterNum()

    def __str__(self)->str:
        return self.actual


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
        print('  Character.py [options]')
        print('Options:')
        print('   NONE')
        return -1
    return 0


if __name__=='__main__':
    import sys
    sys.exit(cmdline(sys.argv[1:]))
