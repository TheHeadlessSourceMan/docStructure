#!/usr/bin/env
# -*- coding: utf-8 -*-
"""
This represents a multipart document.
"""
import typing
from abc import abstractmethod
from docStructure import DocumentBase


class MultiFileDocument(DocumentBase):
    """
    This represents a multi-part document.

    You can retrieve a particular encapsulated document to work on
        MultiFileDocument.documents[name]
    or operate on this directly,which is the same as accessing the
    "default" subdocument.  e.g.
        MultiFileDocument.chapters==
        MultiFileDocument.defaultDocument.chapters==
        MultiFileDocument.documents[self.defaultDocumentName].chapters

    TODO: this should implement "filesystem"
    """

    def __init__(self):
        DocumentBase.__init__(self)
        self._dirty:bool=False
        self.__setattr__=self._setattr_

    @property
    @abstractmethod
    def defaultDocumentName(self)->str:
        """
        return the name of the "real" document representing the actual text
        """

    @property
    def defaultDocument(self)->DocumentBase:
        """
        get the real document representing the actual text
        """
        return self.documents[self.defaultDocumentName]

    @property
    def dirty(self)->bool:
        """
        a multidocument is dirty if it,or any of its child documents,is dirty
        """
        if self._dirty:
            return True
        for doc in self.documents:
            if doc.dirty:
                return True
        return False
    @dirty.setter
    def dirty(self,dirty:bool):
        """
        set whether the overall document is dirty
        """
        self._dirty=dirty

    @abstractmethod
    def loadFile(self,filename:str)->None:
        """
        load a file by name

        :param filename: within this document
        :return data:
        :raise FileNotFoundException:
        """

    @abstractmethod
    def removeFile(self,filename:str)->None:
        """
        remove a file resource

        NOTE: be careful doing this,as it will not remove references to this item.
        """

    def addFile(self,
        asName:typing.Optional[str]=None,
        contents:typing.Optional[str]=None
        )->None:
        """
        adds a new file to the document's resources

        :param asName: internal name/path to call the new data
        :param contents: can be an open file or a string buffer

        NOTE: Will overwrite existing resource so you may want to check
            self.filenames first.
        """
        raise NotImplementedError()

    @property
    @abstractmethod
    def filenames(self)->typing.Iterable[str]:
        """
        returns [filename]
        """

    @property
    @abstractmethod
    def documents(self)->typing.Dict[str,DocumentBase]:
        """
        documents is a dict of {name:documentObject}
        """

    def __getattr__(self,name:str)->str:
        """
        Used to pass a method/property request on to the default document.
        """
        #print("get",name)
        if name not in ['defaultDocument'] and self.defaultDocument is not None:
            try:
                return getattr(self.defaultDocument,name)
            except RuntimeError as e:
                print(name)
                raise e
        return None

    def __setattr__(self,name:str,value:str)->None:
        """
        Used to pass a method/property request on to the default document.
        """
        #print("set",name)
        ignore=['doc','position','parent','include']
        if name[0]!='_' and name not in ignore and self.defaultDocument is not None:
            setattr(self.defaultDocument,name,value)
        else:
            self.__dict__[name]=value

    def assign(self,value:DocumentBase)->None:
        """
        assign a document to direct all get/set to
        """
        if isinstance(value,MultiFileDocument):
            self.documents=value.documents
        DocumentBase.assign(self,value)

    @property
    def children(self)->DocumentBase:
        """
        the document children
        """
        return self.defaultDocument.children

    @property
    def comments(self)->str:
        """
        inline comments in the text
        """
        return self.defaultDocument.comments

    @property
    def html(self)->str:
        """
        document contents in html format
        """
        return self.defaultDocument.html
    @html.setter
    def html(self,html:str):
        self.defaultDocument.html=html

    @property
    def text(self)->str:
        """
        document contents in plain text format
        """
        return self.defaultDocument.text
    @text.setter
    def text(self,text:str):
        self.defaultDocument.text=text


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
                arg[0]=arg[0].lower()
                if arg in ['-h','--help']:
                    printhelp=True
                else:
                    print('ERR: unknown argument "'+arg[0]+'"')
            else:
                print('ERR: unknown argument "'+arg+'"')
    if printhelp:
        print('Usage:')
        print('  MultiFileDocument.py file [commands]')
        print('Commands:')
        print('  [none]')


if __name__=='__main__':
    import sys
    cmdline(sys.argv[1:])