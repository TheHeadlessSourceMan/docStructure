#!/usr/bin/env
# -*- coding: utf-8 -*-
"""
This project breaks down any html-compatible document (which is everything,really) into sentences,
words,parts of speech,etc
"""
import typing
import os
from paths import MimeTypeCompatible,MimeType,UrlCompatible
from docStructure import DocumentBase


class FormatNotFoundException(Exception):
    """
    An exception to be thrown when we have no idea what the format
    of the data is.
    """

    def __init__(self,ext:str=None,mimeType:str=None):
        """
        :param ext: The file extension(s) we were looking for
        :param mimeType: The mime type(s) we were looking for
        """
        err='Format not found!'
        if ext is not None:
            err=err+' .'+str(ext)
        if mimeType is not None:
            err=err+' '+str(mimeType)
        Exception.__init__(self,err)


class Document(DocumentBase):
    """
    This class represents an entire doc.

    It forwards all calls to internal delegate which can be swapped in/out with
        anything derived from DocumentBase.  In fact,"loading" an object
        with a "html" or "text" data member will automatically wrap it into a
        htmlDocument and use it!

    NOTE: New type implementors should not derive from this document,but rather
        from DocumentBase or MultiFileDocument
    """

    def __init__(self,
        dataSource:typing.Optional[UrlCompatible]=None,
        data:typing.Optional[str]=None,
        mimeType:typing.Optional[MimeTypeCompatible]=None):
        """
        :param dataSource: can be:
            * any docStructure.DocumentBase derived object
            * a file name
            * a URL
            * a file-like object
            * '-' to specify stdin
            * None if data is to be passed in instead
            * any object with a .text or .html data member
                (will be wrapped in a HtmlDocument object)
        :param data: if dataSource is None,pass in a data buffer can be:
            * any docStructure.DocumentBase derived object
            * a string of data bytes
            * any object with a .text or .html data member
                (will be wrapped in a HtmlDocument object)
        :param mimeType: since we may not have a dataSource extension to go off,
            specify the file type
        """
        self._delegateDocument=None
        DocumentBase.__init__(self)
        self.load(dataSource,data,mimeType)

    def __getattr__(self,name:str):
        """
        Used to pass a method/property request on to the current delegate document.
        """
        if name not in ('_delegateDocument') and self.__dict__['_delegateDocument'] is not None:
            return getattr(self._delegateDocument,name)
        return super(Document,self).__getattribute__(name)

    def _pathinfo(self,path:str):
        """
        return info about a url or system path.

        Gives you protocol,extension
        where protocol is always defined and extension can be None
        """
        ext=None
        proto=path.split('://',1)
        if len(proto)>1 and proto[0]!='file':
            # url
            name=path.rsplit('/',1)[-1].split('.',1)
            if len(name)>1:
                ext=name[-1]
        else:
            # file
            if path.startswith('file://'):
                path=path.split('://',1)[-1]
                if os.sep!='/':
                    path=path.replace('/',os.sep)
            else:
                proto='file'
            name=path.rsplit(os.sep,1)[-1].rsplit('.',1)
            if len(name)>1:
                ext=name[-1]
        return proto,ext

    def load(self,
        dataSource:UrlCompatible,
        data:typing.Optional[str]=None,
        mimeType:typing.Optional[MimeTypeCompatible]=None)->None:
        """
        Load a new document.

        :param dataSource: can be:
            * any docStructure.DocumentBase derived object
            * a file name
            * a URL
            * a file-like object
            * '-' to specify stdin
            * None if data is to be passed in instead
            * any object with a .text or .html data member
                (will be wrapped in a HtmlDocument object)
        :param data: if dataSource is None,pass in a data buffer can be:
            * any docStructure.DocumentBase derived object
            * a string of data bytes
            * any object with a .text or .html data member
                (will be wrapped in a HtmlDocument object)
        :param mimeType: since we may not have a dataSource extension to go off,
            specify the file type

        :raises FormatNotFoundException: whenever we can't arrive at something loadable
        """
        ext=None
        worked=False
        # boil everything down to either a data string or dataSource
        if isinstance(dataSource,DocumentBase):
            self._delegateDocument=dataSource
            worked=True
        elif isinstance(data,DocumentBase):
            self._delegateDocument=data
            worked=True
        else:
            if hasattr(dataSource,'read'): # file-like object
                data=dataSource.read()
                filename=dataSource.name
            elif hasattr(dataSource,'html'): # has html data member
                data=dataSource.html
                mimeType='text/html'
                filename=None
            elif hasattr(dataSource,'text'): # has text data member
                data=dataSource.text
                mimeType='text/plain'
                filename=None
            elif hasattr(data,'html'): # has html data member
                data=data.html
                mimeType='text/html'
                filename=None
            elif hasattr(data,'text'): # has text data member
                data=data.text
                mimeType='text/plain'
                filename=None
            # Now expand the concept further
            if data is not None: # load the data
                from docStructure import htmlDocument
                self.mimeType=mimeType
                self._delegateDocument=htmlDocument.HtmlDocument()
                self._delegateDocument.filename=filename
                if isinstance(data,(bytes,bytearray)):
                    data=data.decode('utf-8','ignore')
                if mimeType=='text/plain':
                    self._delegateDocument.text=data
                    worked=True
                elif mimeType=='text/html':
                    self._delegateDocument.html=data
                    worked=True
            elif isinstance(dataSource,str): # load the dataSource
                worked=self._loadByFilename(dataSource,mimeType,data)
        if not worked:
            raise FormatNotFoundException(ext,mimeType)

    def _loadByFilename(self,filename:str,mimeType:MimeType,data:str):
        worked=False
        proto,ext=self._pathinfo(filename)
        if ext in ('htm','html','txt'):
            mimeType='text/html'
            if ext=='txt':
                mimeType='text/plain'
            if proto!='file':
                raise NotImplementedError(proto)
            f=open(filename,'rb')
            self.load(f,None,mimeType)
            return True
        try:
            import pyformatgenie
        except ImportError as e:
            print('WARN: Should probably have pyformatgenie and some plugins installed!')
            raise FormatNotFoundException(ext,mimeType) from e
        pfg=pyformatgenie.PyFormatGenie()
        formats=pfg.findFormats(filename,mimeType,data)
        for fmt in formats:
            if True:#try:
                ob=fmt.load(filename)
            #except Exception,e:
                #print('ERR:'+str(e)+'\n\tWhen using type "'+fmt.name+'" to load "'+filename+'"')
                #continue
            if isinstance(ob,DocumentBase):
                self.mimeType=ob.mimeType
                self._delegateDocument=ob
                worked=True
                break
            elif hasattr(ob,'html') or hasattr(ob,'text'):
                from docStructure import htmlDocument
                if hasattr(ob,'html'):
                    mimeType='text/html'
                else:
                    mimeType='text/plain'
                self.mimeType=mimeType
                self._delegateDocument=htmlDocument.HtmlDocument()
                self._delegateDocument.filename=filename
                if mimeType=='text/plain':
                    self._delegateDocument.text=data
                elif mimeType=='text/html':
                    self._delegateDocument.html=data
                worked=True
                break
            else:
                print('unable to get text document-like data out of %s from %s'%(
                    ob.__class__.__name__,ob.__class__.__module__))
                print(dir(ob))
                errStr=ob.__class__.__name__+' - No way to use this type of file!'
                raise Exception(errStr)
        return worked


def cmdline(args):
    """
    Run the command line

    :param args: command line arguments (WITHOUT the filename)
    """
    printhelp=False
    if not args:
        printhelp=True
    else:
        doc=None
        for arg in args:
            if arg.startswith('-'):
                arg=[a.strip() for a in arg.split('=',1)]
                arg[0]=arg[0].lower()
                if arg in ['-h','--help']:
                    printhelp=True
                elif arg[0]=='--wordcount':
                    print(doc.wordCount)
                elif arg[0]=='--sentencecount':
                    print(doc.sentenceCount)
                elif arg[0]=='--paragraphcount':
                    print(doc.paragraphCount)
                elif arg[0]=='--chaptercount':
                    print(doc.chapterCount)
                elif arg[0]=='--words':
                    print(doc.words[int(arg[1])])
                elif arg[0]=='--sentences':
                    print(doc.sentences[int(arg[1])])
                elif arg[0]=='--paragraphs':
                    print(doc.paragraphs[int(arg[1])])
                elif arg[0]=='--chapters':
                    print(doc.chapters[int(arg[1])])
                elif arg[0]=='--chapdesc':
                    chapNo=None
                    if len(arg)>1:
                        chapNo=int(arg[1])
                    i=None
                    for chapter in doc.chapters:
                        if chapNo is None or i==chapNo:
                            print('Chapter '+str(i)+': '+chapter.title)
                            for line in chapter.description.split('\n'):
                                print('   '+line)
                elif arg[0]=='--html':
                    if len(arg)>1:
                        f=open(arg[1],'wb')
                        f.write(doc.html)
                        f.close()
                    else:
                        print(doc.html)
                elif arg[0]=='--text':
                    if len(arg)>1:
                        f=open(arg[1],'wb')
                        f.write(doc.text)
                        f.close()
                    else:
                        print(doc.text)
                elif arg[0]=='-':
                    print('In [STDIN]:')
                    doc=Document(arg)
                else:
                    print('ERR: unknown argument "'+arg[0]+'"')
            else:
                print('In',arg,':')
                doc=Document(arg)
    if printhelp:
        print('Usage:')
        print('  Document.py file [commands]')
        print('Where file can be:')
        print('  filename or url ... html,text,or anything registered with pyformatgenie')
        print('  - ................. for stdin')
        print('Commands:')
        print('  --wordCount ....... how many words')
        print('  --sentenceCount ... how many sentences')
        print('  --paragraphCount .. how many paragraphs')
        print('  --chapterCount .... how many chapters')
        print('  --word[n] ......... get words')
        print('  --sentence[n] ..... get sentences')
        print('  --paragraph[n] .... get paragraphs')
        print('  --chapter[n] ...... get chapters')
        print('  --chapdesc[n] ..... get chapter descriptions')
        print('  --text[=file] ..... convert to plain text (no file=stdout)')
        print('  --html[=file] ..... convert to html (no file=stdout)')


if __name__=='__main__':
    import sys
    cmdline(sys.argv[1:])