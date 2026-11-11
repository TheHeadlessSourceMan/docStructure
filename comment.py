#!/usr/bin/env
# -*- coding: utf-8 -*-
"""
This class represents a comment.

This inserts a logical level between Chapter and Paragraph items.

NOTE: Its contents are outside of the document flow so comment.words
will neither show up in comment.chapter.words,
nor will it increase word count.
"""
import typing
from docStructure import DocFrag
if typing.TYPE_CHECKING:
    from .chapter import Chapter
    from .document import Document


class Comment(Chapter): # acts like an out-of-flow chapter
    """
    This class represents a comment.

    This inserts a logical level between Chapter and Paragraph items.

    NOTE: Its contents are outside of the document flow so comment.words
    will neither show up in comment.chapter.words,
    nor will it increase word count.
    """

    def __init__(self,doc:"Document",parent:DocFrag,position:int):
        """
        :param doc: the document this paragraph belongs to
        :param parent: the parent object in the hierarchy
        :param position: the actual location of this item
        """
        Chapter.__init__(self,doc,parent,position)
        self.location=position
        self.includeInFinalDocument=False

    def chapterNum(self)->int:
        """
        chapter number within document
        """
        return self.chapter.chapterNum()

    @property
    def chapters(self # type: ignore
        )->typing.Iterable["Chapter"]:
        """
        get all chapters related to this frag

        In a practical sense,this will be [theParentChapter]
        """
        if self.parent is None:
            return []
        if isinstance(self.parent,Chapter): # type: ignore
            return [self.parent]
        return self.parent.chapters
    @property
    def chapter(self)->"Chapter":
        """
        get the parent chapter of this comment

        This is because you probably want to do things
        like get all of the comments for a chapter.
        """
        for chapter in self.chapters:
            return chapter
        raise Exception("No parent chapter found for this comment")


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
                kw=[a.strip() for a in arg.split('=',1)]
                if kw[0] in ('-h','--help'):
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
        return -1
    return 0


if __name__=='__main__':
    import sys
    sys.exit(cmdline(sys.argv[1:]))
