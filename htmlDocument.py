#!/usr/bin/env
# -*- coding: utf-8 -*-
"""
This allows opening html as a word processor document,and/or
serves as an example for implementing other formats.
"""
import typing
import os
import lxml.html
import lxml.etree
import docStructure
from docStructure import DocumentBase, Chapter, DocFrag, Comment


class HtmlChapter(Chapter):
    """
    Figure out how a chapter looks in an html document
    """

    def __init__(self,
        parent:DocFrag,
        titleNode:str,
        contentNodes:typing.Iterable[lxml.etree.ElementTree],
        position:typing.Tuple[int,int]):
        """
        :param parent: the parent object in the hierarchy
        :param titleNode: xml node containing the chapter title
        :param contentNodes: xml nodes containing the guts of the chapter
        :param position: the actual location of this item
        """
        self.titleNode=None # don't allow the Chapter object to smash this
        # needs to be available to chapter constructor
        Chapter.__init__(self,parent,parent,position)
        self.titleNode=titleNode
        self._text=None
        self.contentNodes=list(contentNodes)
        self._position=None
        print(self.text)

    @property
    def position(self)->typing.Tuple[int,int]:
        """
        Override position so we can base it on the text length.

        TODO: I'm not sure I like doing it this way.
        """
        return (self._position[0],len(self))
    @position.setter
    def position(self,position:typing.Tuple[int,int]):
        self._position=position

    @property
    def title(self)->str:
        """
        the chapter title
        """
        # this first way gets sub tag text but unfortunately comments as well
        #return ''.join(self.titleNode.itertext())
        return self.titleNode.text.strip()
    @title.setter
    def title(self,title:str):
        if self.titleNode is not None:
            self.titleNode.text=title.strip()

    @property
    def comments(self)->typing.Iterable[str]:
        """
        get all comments within this chapter

        NOTE: every overall comment without a specific location will
            show up at the starting location of the chapter
        """
        if self._comments is None:
            self._comments=self.parent.commentsInRange(self._position)
        return self._comments

    def __len__(self)->int:
        return len(self.text)

    @property
    def html(self)->str:
        ret=[]
        for node in self.contentNodes:
            ret.append(lxml.etree.tostring(node,encoding='UTF-8',method="text"))
        return ''.join(ret)

    @property
    def text(self)->str:
        """
        Get plaintext representation.

        # TODO: I don't think I need this as the DocFrag object will convert
        # the html value automatically
        """
        if self._text is None:
            ret:typing.List[str]=[]
            for node in self.contentNodes:
                if isinstance(node,lxml.etree._ElementStringResult):
                    val=node
                elif isinstance(node,lxml.etree._ElementUnicodeResult):
                    val=str(node) # errors='replace' is unnecessary because it is valid unicode
                elif isinstance(node,lxml.html.HtmlComment):
                    continue
                else:
                    if node.tag[0]=='h' and node.tag[1].isdigit():
                        continue
                    val=lxml.etree.tostring(node,encoding='UTF-8',method="text").decode('utf-8',errors="ignore")
                    if node.tag in ('pre','br','p','hr','table','tr','div'):
                        # assume div is a block element
                        val=val+'\n'
                    elif node.tag not in ('i','u','b','td'):
                        print('Unknown tag',node.tag)
                        raise Exception()
                if not isinstance(val,str):
                    val=str(val,errors='replace')
                ret.append(val)
            self._text=''.join(ret)
        return self._text


class HtmlDocument(DocumentBase):
    """
    This allows opening html as a word processor document,and/or
    serves as an example for implementing other formats.


    TODO: here is the problem.  I have this dataProvider scheme that the child
        DocFrags want to use to get text to parse,but this class reads the html
        file directly.  Something about this scheme is convoluted
        and all-around bad.
    """

    # define which class to use for creating chapters (useful for derived classes)
    ChapterClass=HtmlChapter

    def __init__(self,filename:typing.Optional[str]=None,data:typing.Optional[str]=None):
        """
        :param filename: can be a filename or common form of url. SEE Load()
        :param data: if you want to feed in the document's html directly rather than loading it
            (if the first non-whitespace character is not '<' will decode as plain text)

        NOTE: if data and filename are given,will not load filename,but will treat data
            like it came from filename
        """
        DocumentBase.__init__(self)
        self._text:typing.Optional[str]=None
        self._html:typing.List[str]=[]
        self._lineStarts:typing.List[int]=[]
        self._author:typing.Optional[str]=None
        self._title:typing.Optional[str]=None
        self._children=None
        self._wrapped=None
        self._filename:typing.Optional[str]=None
        self._dataProvider=self
        self._comments:typing.Optional[str]=None
        self._etree:typing.Optional[lxml.etree.ElementTree]=None
        if filename is not None or data is not None:
            self.load(filename,data)

    @property
    def etree(self)->lxml.etree.ElementTree:
        """
        get an lxml etree object to mess with
        """
        if self._etree is None:
            self._etree=lxml.etree.HTML(self.html)
        return self._etree

    def load(self,
        filename:typing.Optional[str]=None,
        data:typing.Optional[str]=None
        )->None:
        """
        Load document data.

        :param filename: can be:
            * a docStructure.Document derived object
            * a file name
            * a URL
            * a file-like object
            * '-' to specify stdin
            * None if data is to be passed in instead
        :param data: if you want to feed in the document's html directly rather than loading it
            (if the first non-whitespace character is not '<' will decode as plain text)

        NOTE: if data and filename are given,will not load filename,but will treat data
            like it came from filename
        """
        self._etree=None
        self._html=[]
        isHtml=False
        if data is not None:
            data=data.strip()
            if data and data[0]=='<':
                isHtml=True
        elif hasattr(filename,'html'):
            # looks like we're wrapping it
            self._wrapped=filename
            self._filename=None
            data=self._wrapped.html
            isHtml=True
        elif hasattr(filename,'text'):
            # looks like we're wrapping it
            self._wrapped=filename
            self._filename=None
            data=self._wrapped.html
        elif filename is not None:
            f=open(filename,'rb')
            data=f.read()
            try:
                data=data.decode('utf-8','ignore')
            except UnicodeDecodeError:
                data=data.decode('ansi')
            data=data.strip()
            f.close()
            if data and data[0]=='<':
                isHtml=True
        data=data.replace('\r\n','\n') # windows line endings are lame
        if not isHtml:
            from docStructure import txt2html
            data=txt2html(data)
        self._html=data.split('\n')

    def save(self,asFilename:typing.Optional[str]=None)->None:
        """
        asFilename can be:
            * None to save over existing
            * an html filename
            * any file type a wrapped object supports
            * a file-like object (if non-wrapped)
            * "-" for stdout (if non-wrapped)
        """
        if asFilename is None or asFilename.rsplit('.',1)[-1] not in ('htm','html','xhtml'):
            if self._wrapped is not None and hasattr(self._wrapped,'filename'):
                return self._wrapped.filename.save(asFilename)
        if asFilename is None:
            asFilename=self.filename
        elif hasattr(asFilename,'write'):
            asFilename.write(self.html.encode('utf-8'))
        elif asFilename=='-':
            print(self.html)
        else:
            f=open(asFilename,'wb')
            f.write(self.html.encode('utf-8'))
            f.close()
        return True

    @property
    def filename(self)->str:
        """
        :return: the current filename,or None if there isn't one
        """
        if self._wrapped is not None and hasattr(self._wrapped,'filename'):
            return self._wrapped.filename
        return self._filename
    @filename.setter
    def filename(self,filename:str):
        self._filename=filename

    def _findLocation(self,
        xmltag:typing.Union[lxml.etree._Element,typing.Iterable[lxml.etree._Element]]
        )->typing.Union[int,typing.Tuple[int,int]]:
        """
        Find the location of the given tag.

        :param xmltag: can be a single tag or an array of them

        :returns: len,
            (startLine,startCharOffs),
            (endLine,endCharOffs),
            (startAbsoluteChar,endAbsoluteChar)

        NOTE: all returned values are zero-based,that is,if you call
            the first line of the document "Line 1",you'll want to startLine+1
        """
        if self._html is None:
            _=self.html
        if isinstance(xmltag,lxml.etree._Element): # make it a list if it isn't already one
            xmltag=[xmltag]
        startTag=xmltag[0]
        endTag=xmltag[-1]
        if isinstance(startTag,str):
            startTag=startTag.getparent()
        if isinstance(endTag,str):
            endTag=endTag.getparent()
        s=[]
        for tag in xmltag:
            if isinstance(tag,(str,lxml.etree._ElementStringResult)):
                s.append(tag)
            else:
                xml=lxml.etree.tostring(tag,pretty_print=True)
                if isinstance(xml,bytes):
                    xml=xml.decode('utf-8','ignore')
                s.append(xml)
        s=''.join(s).rstrip()
        lenS=len(s)
        s=s.split('\n')
        startLine:int=startTag.sourceline-1
        numNewlines=len(s)-1
        endLine=numNewlines-startLine
        startCharOffs=self._html[startLine].rfind(s[0])
        if startLine==endLine:
            endCharOffs=startCharOffs+lenS
        else:
            #print('XHECK:',len(s),numNewlines,'|',len(self._html),startLine,endLine)
            #print(s)
            content=s[numNewlines]
            endCharOffs=self._html[endLine].find(content)+len(content)
        lineStarts=list(self.lineStarts)
        startAbsoluteChar=lineStarts[startLine]+startCharOffs
        endAbsoluteChar=lineStarts[endLine]-endCharOffs
        if endCharOffs-startCharOffs!=lenS:
            print('problem:',lenS,(startLine,startCharOffs),
                (endLine,endCharOffs),(startAbsoluteChar,endAbsoluteChar))
            #raise Exception("Math is hard. :_(")
        return (
            lenS,
            (startLine,startCharOffs),
            (endLine,endCharOffs),
            (startAbsoluteChar,endAbsoluteChar))

    def getElementsByTagName(self,tagName:str
        )->typing.Iterable[lxml.etree._Element]:
        """
        get all html elements by their tag name
        """
        return self.etree.find(tagName) # same as getElementByTagName
    def getElementByTagName(self,tagName)->lxml.etree._Element:
        """
        same as getElements only gets exactly one (or None)
        """
        elements=self.getElementsByTagName(tagName)
        if not elements:
            return None
        return elements[0]

    def makePathExist(self,path:typing.List[str])->lxml.etree._Element:
        """
        make the given xml path exist,either by getting
        existing,or creating missing elements

        NOTE: path is smart enough you can leave off html/head/ or html/body/
        """
        if isinstance(path,str):
            path=path.split('/')
        if path[0]!='html':
            if path[0] not in ['head','body']:
                if path[0] in ['script','style','link','title']:
                    path.insert(0,'head')
                else:
                    path.insert(0,'body')
            path.insert(0,'html')
        el=self.etree
        for level in path:
            els=el.find(level) # same as getElementByTagName
            if not els:
                el=el.makeelement(level)
            else:
                el=els[0]
        return el


    @property
    def lineStarts(self)->typing.Iterable[int]:
        """
        Figure out where the start of each line is
        """
        if not self._lineStarts:
            i=0
            for line in self._html:
                self._lineStarts.append(i)
                i+=len(line)
        return self._lineStarts

    @property
    def html(self)->str:
        """
        get the document as html
        """
        if self._html is None:
            self._html=lxml.etree.tostring(self.etree,method='xml',
                encoding='unicode',pretty_print=True).split('\n')
        return '\n'.join(self._html)
    @html.setter
    def html(self,html:str):
        if self._wrapped is not None:
            self._wrapped.html=html
        else:
            self.load(data=html)

    @property
    def text(self)->str:
        """
        :return: the contents re-formatted as text
        """
        if self._text is None:
            ret=[]
            i=1
            for c in self.chapters:
                title=c.title
                if title is None:
                    title='Chapter '+str(i)
                ret.append(title)
                ret.append(len(title)*'-')
                #ret.append(c.text)
                ret.append('')
                i+=1
            self._text='\n'.join(ret)
        return self._text
    @text.setter
    def text(self,text:str):
        from docStructure import txt2html
        self.html=txt2html(text)
        self._text=text

    def _chapterSplit(self,
        element:lxml.etree._Element,
        headingLevel:str='h1'
        )->typing.Iterable[typing.Tuple[lxml.etree._Element,lxml.etree._Element]]:
        """
        Helper function to split a document into chapters when formatted such as:
            <h2>chapter title</h2>
            chapter contents
            <h2>next chapter title</h2>
            ...

        It is designed such that someday you can have different heading levels
            for an engineering style document

        :param element: the starting xml element
        :param headingLevel: the level we are operating at
        """
        ret=[]
        nodes=self.etree.xpath(f'//*/{headingLevel}')
        for i,titleNode in enumerate(nodes):
            #print('FOUND',titleNode.text)
            xpath=f'/html/body/{headingLevel}[{i+1}]'
            xpath=f'{xpath}/following-sibling::node()[not(self::{headingLevel})]'
            xpath=f'{xpath}[count(preceding-sibling::{headingLevel})={i+1}]'
            contentNodes=element.xpath(xpath)
            ret.append((titleNode,contentNodes))
        return ret

    @property
    def author(self)->str:
        """
        retrieve the author info from the Author <meta> tag
        """
        if self._author is None:
            xml=self.etree
            if xml is None:
                return None
            for el in xml.xpath("//meta[contains(@name,'Author')]"):
                self._author=el.attrib['content']
            if self._title is None and self.filename is not None:
                # attempt to get it from the filename
                x=self.filename.rsplit(os.sep,1)[-1].split('.',1)[0].split('-',1)
                if len(x)>1:
                    x=x[1].replace('_',' ').strip()
                    if x:
                        self._title=x
        return self._author
    @author.setter
    def author(self,value:str):
        self._author=value
        # TODO: save to file and mark dirty

    @property
    def title(self)->str:
        """
        the title of the document from the <title> tag

        If not found,try to use the filename of the document
        """
        if self._title is None:
            xml=self.etree
            if xml is None:
                return None
            for el in xml.xpath("//title"):
                self._title=el.text
            if self._title is None and self.filename is not None:
                # attempt to get it from the filename
                x=self.filename.rsplit(os.sep,1)[-1].split('.',1)[0]
                x=x.split('-',1)[0].replace('_',' ').strip()
                if x:
                    self._title=x
        return self._title
    @title.setter
    def title(self,value:str):
        self._title=value
        # TODO: save to file and mark dirty

    @property
    def children(self)->typing.Iterable[Chapter]:
        """
        splits children (aka chapters) from the html doc
        """
        if self._children is None:
            self._children=[]
            body=self.etree.xpath('//*/body')[0]
            position=None
            # first check <h1> then <h2> and so on until we get something split
            for level in range(1,9):
                chapters=self._chapterSplit(body,'h'+str(level))
                if chapters:
                    for title,contents in chapters:
                        if position is None:
                            _,_,_,position=self._findLocation(title)
                            position=[position[0],position[0]]
                        _,_,_,charOffsets=self._findLocation(contents)
                        chap=self.ChapterClass(self,title,contents,[0,0])
                        position[1]=charOffsets[-1]
                        chap.position=(position[0],position[1])
                        self._children.append(chap)
                        position[0]=position[1]
                    break
        return self._children
    @children.setter
    def children(self,children:typing.Iterable[Chapter]):
        self._children=children

    @property
    def comments(self)->typing.Iterable[Comment]:
        """
        get all comments
        """
        if self._comments is None:
            self._comments=[]
            for comment in self.etree.xpath('//*/comment()'):
                _,_,_,position=self._findLocation(comment)
                comment=docStructure.Comment(self.doc,self,position)
                self._comments.append(comment)
        return self._comments

    def commentsInRange(self,position:typing.Tuple[int,int])->typing.Iterable[Comment]:
        """
        get all comments within a prescribed range

        :param position: an array or tuple like (start,end)
        """
        found=[]
        print(position)
        for comment in self.comments:
            if comment.position[0]>=position[0] and comment.position[1]<=position[1]:
                found.append(comment)
        return found


def cmdline(args:typing.Iterable[str])->int:
    """
    Run the command line

    :param args: command line arguments (WITHOUT the filename)
    """
    printhelp=False
    if not args:
        printhelp=True
    else:
        htmlDocument=None
        for arg in args:
            if arg.startswith('-'):
                arg=[a.strip() for a in arg.split('=',1)]
                if arg[0] in ['-h','--help']:
                    printhelp=True
                elif arg[0]=='--find':
                    if htmlDocument is None:
                        print('ERR: no document loaded yet')
                    else:
                        print(htmlDocument.find(arg[1]))
                elif arg[0]=='--chapters':
                    print('Chapters:')
                    for c in htmlDocument.chapters:
                        print('  ',c.title)
                elif arg[0]=='--json':
                    print(htmlDocument.json)
                elif arg[0]=='--text':
                    print(htmlDocument.text)
                else:
                    print('ERR: unknown argument "'+arg[0]+'"')
            else:
                htmlDocument=HtmlDocument(arg)
    if printhelp:
        print('Usage:')
        print('  htmlDocument.py file.html [options]')
        print('Options:')
        print('  --find=html ..... find the next occourence of given html')
        print('  --chapters ...... list all the chapters')
        print('  --json .......... dump a json representation of the doc\'s structure')
        print('  --text .......... dump a plaintext representation of the doc')


if __name__=='__main__':
    #import sys
    #cmdline(sys.argv[1:])
    htd=HtmlDocument(r'C:\backed_up\writing\writing projects\Moast Unusual\Third Crown\Third Crown.html')
    print(htd.text)