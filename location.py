#!/usr/bin/env
# -*- coding: utf-8 -*-
"""
Tools for finding and tracking doc location of text
"""
import typing
if typing.TYPE_CHECKING:
    from docStructure import Document


class Location:
    """
    Represents a location within a document
    """

    def __init__(self,doc:"Document",startPosition:int=0,length:int=0):
        """
        :param doc: the document
        :param startPosition: the actual location of this item
        """
        self.doc=doc
        if startPosition is None:
            raise Exception("Location with no position")
        self.startPosition=startPosition
        self._length=length

    @property
    def position(self)->typing.Tuple[int,int]:
        """
        position of this text fragment
        """
        return (self.startPosition,self.endPosition)

    @property
    def endPosition(self)->int:
        """
        where this text fragment ends
        """
        return self.startPosition+self._length
    @endPosition.setter
    def endPosition(self,endPosition:int):
        if endPosition<self.startPosition:
            sp=self.startPosition
            self.startPosition=endPosition
            endPosition=sp
        self._length=self.startPosition-endPosition

    def getLocationString(self)->str:
        """
        return the location as a user-readable string
        """
        return f'{self.doc.name}@{self.startPosition}-{self.endPosition}' # noqa: E501

    def __repr__(self)->str:
        """
        NOTE: This will probably be hidden by derived classes
        """
        return self.getLocationString()

    @property
    def startLine(self)->int:
        """
        the (line,char_offset) of the start of this element

        NOTE: in wrapped text and marked-up documents this is not necessirily
        the line the reader is seeing,but is instead the line in the source doc
        descriptiveLocation() might be more what you're looking for
        """
        return self.doc.offsToLine(self.startPosition)
    line=startLine

    @property
    def endLine(self)->int:
        """
        the (line,char_offset) of the end of this element

        NOTE: in wrapped text and marked-up documents this is not necessirily
        the line the reader is seeing,but is instead the line in the source doc
        descriptiveLocation() might be more what you're looking for
        """
        return self.doc.offsToLine(self.endPosition)

    # ---- implement comparison operators so we can locate things
    def __eq__(self,other:"Location")->bool:
        """
        comparison operators
        """
        if isinstance(other,Location):
            return other.position[0]==self.position[0] \
                and other.position[1]==self.position[1]
        return self.position[0]<=other<=self.position[1]
    def __ne__(self,other:"Location")->bool:
        """
        comparison operators
        """
        return not self==other
    def __lt__(self,other:"Location")->bool:
        """
        comparison operators
        """
        if isinstance(other,Location):
            other=other.position[0]
        return other<self.position[1]
    def __gt__(self,other:"Location")->bool:
        """
        comparison operators
        """
        if isinstance(other,Location):
            other=other.position[1]
        return other>self.position[0]
    def __le__(self,other:"Location")->bool:
        """
        comparison operators
        """
        if isinstance(other,Location):
            other=other.position[0]
        return other<=self.position[0]
    def __ge__(self,other:"Location")->bool:
        """
        comparison operators
        """
        if isinstance(other,Location):
            other=other.position[1]
        return other>=self.position[1]

    def __len__(self)->int:
        """
        the size of this text fragment
        """
        return self._length

    def length(self)->int:
        """
        the size of this text fragment
        """
        return self._length


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
        print('  Location.py [options]')
        print('Options:')
        print('   NONE')


if __name__=='__main__':
    import sys
    cmdline(sys.argv[1:])
