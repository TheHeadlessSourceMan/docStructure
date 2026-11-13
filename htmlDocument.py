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
from paths import asUrl,Url,UrlCompatible
from htmlTools import Html,PlaintextCompatible
from docStructure import DocumentBase, Chapter, DocFrag
if typing.TYPE_CHECKING:
    from .document import Document
    from .comment import Comment
    from htmlTools.html import EtreeElement


class HtmlChapter(Chapter):
    """
    Figure out how a chapter looks in an html document
    """

    @typing.overload
    def __init__(self, # type: ignore
        parent:DocFrag,
        titleNodeOrChapter:str,
        contentNodes:typing.Iterable[EtreeElement],
        position:typing.Tuple[int,int]):
        ...
    @typing.overload
    def __init__(self, # type: ignore
        parent:DocFrag,
        titleNodeOrChapter:Chapter,
        contentNodes:None=None,
        position:None=None):
        ...
    def __init__(self,
        parent:DocFrag,
        titleNodeOrChapter:typing.Union[str,Chapter],
        contentNodes:typing.Optional[typing.Iterable["EtreeElement"]]=None,
        position:typing.Optional[typing.Tuple[int,int]]=None):
        """
        :param parent: the parent object in the hierarchy
        :param titleNode: xml node containing the chapter title
        :param contentNodes: xml nodes containing the guts of the chapter
        :param position: the actual location of this item
        """
        self._text:typing.Optional[str]=None
        self._position:typing.Optional[typing.Tuple[int,int]]=None
        self._comments:typing.Optional[typing.List[str]]=None
        self.contentNodes:typing.List["EtreeElement"]=[]
        self.titleNode:typing.Optional["EtreeElement"]=None # don't allow the Chapter object to smash this because it needs to be available to chapter constructor # noqa: E501 # pylint: disable=line-too-long
        if isinstance(titleNodeOrChapter,Chapter):
            position=titleNodeOrChapter.position
            contentNodes=Html(titleNodeOrChapter.html).etree
            self.titleNode=Html(titleNodeOrChapter.title).etree
            if hasattr(titleNodeOrChapter,'comments'):
                titleNodeOrChapter.comments=typing.cast(
                    typing.Union[str,typing.Iterable[str]],
                    titleNodeOrChapter.comments) # type: ignore
                if isinstance(titleNodeOrChapter.comments,str):
                    self._comments=[titleNodeOrChapter.comments]
                else:
                    self._comments=list(titleNodeOrChapter.comments)
        elif position is None or contentNodes is None:
            raise TypeError("contentNodes and position must be provided if titleNodeOrChapter is not a Chapter") # noqa: E501 # pylint: disable=line-too-long
        else:
            self.titleNode=titleNodeOrChapter
            self.contentNodes=list(contentNodes)
        Chapter.__init__(self,parent.doc,parent,position)
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
        return self.titleNode.text.strip() # type: ignore
    @title.setter
    def title(self,title:str): # type: ignore
        if self.titleNode is not None: # type: ignore
            self.titleNode.text=title.strip() # type: ignore

    @property
    def comments(self)->typing.Iterable["Comment"]:
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
    def html( # type: ignore
        self)->str:
        """
        Get the HTML representation of the chapter content.
        """
        ret:typing.List[str]=[]
        for node in self.contentNodes:
            ret.append(lxml.etree.tostring(
                node,encoding='UTF-8',method="text"))
        return ''.join(ret)

    @property
    def text(self # type: ignore
        )->str:
        """
        Get plaintext representation.

        # TODO: I don't think I need this as the DocFrag object will convert
        # the html value automatically
        """
        if self._text is None:
            from htmlTools.html import (
                EtreeElementStringResult)
            ret:typing.List[str]=[]
            for node in self.contentNodes:
                if isinstance(node,EtreeElementStringResult):
                    val=node
                elif isinstance(node,EtreeElementStringResult):
                    val=str(node)
                elif isinstance(node,lxml.html.HtmlComment):
                    continue
                else:
                    if node.tag[0]=='h' and node.tag[1].isdigit():
                        continue
                    val=lxml.etree.tostring(
                        node,encoding='UTF-8',method="text")\
                        .decode('utf-8',errors="ignore")
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


class HtmlDocument(DocumentBase,Html):
    """
    This allows opening html as a word processor document,and/or
    serves as an example for implementing other formats.

    Document semantics (DocumentBase) win over htmlTools.Html where they clash;
    Html contributes its helpers (xpath, cssSelect, links, soup, ...).


    TODO: here is the problem.  I have this dataProvider scheme that the child
        DocFrags want to use to get text to parse,but this class reads the html
        file directly.  Something about this scheme is convoluted
        and all-around bad.
    """

    # define which class to use for creating chapters
    # (useful for derived classes)
    ChapterClass=HtmlChapter

    def __init__(self,
        filename:typing.Union[None,UrlCompatible,"Document"]=None,
        data:typing.Optional[str]=None):
        """
        :param filename: can be a filename or common form of url. SEE Load()
        :param data: if you want to feed in the document's html directly
            rather than loading it (if the first non-whitespace character
            is not '<' will decode as plain text)

        NOTE: if data and filename are given, will not load filename, but
        will treat data like it came from filename
        """
        DocumentBase.__init__(self)
        Html.__init__(self)
        self._text:typing.Optional[str]=None
        self._lineStarts:typing.List[int]=[]
        self._author:typing.Optional[str]=None
        self._title:typing.Optional[str]=None
        self._children:typing.Optional[typing.List["HtmlChapter"]]=None
        self._wrapped=None
        self._dataProvider=self
        self._comments:typing.Optional[typing.List[Comment]]=None
        if filename is not None or data is not None:
            self.load(filename,data)

    def assign(self, # pylint: disable=arguments-renamed
        value:typing.Any=None,
        html:typing.Any=None,
        text:typing.Any=None
        )->None:
        """
        Supports both the DocumentBase and htmlTools.Html calling styles.

        :param value: DocumentBase semantics: a document, or anything
            that can create an HtmlDocument
        :param html: Html semantics: anything html compatible
        :param text: Html semantics: anything plain text compatible

        If none are given, the document is emptied.
        """
        if value is not None:
            DocumentBase.assign(self,value)
            return
        self.clean()
        self._lineStarts=[]
        self._html=""
        if html is not None:
            self.html=html
        elif text is not None:
            self.text=text

    def load(self, # pylint: disable=arguments-renamed
        source:typing.Union[None,UrlCompatible,"Document"]=None,
        data:typing.Optional[str]=None
        )->None:
        """
        Load document data.

        :param source: can be:
            * a docStructure.Document derived object
            * a file name
            * a URL
            * a file-like object
            * '-' to specify stdin
            * None if data is to be passed in instead
        :param data: if you want to feed in the document's html directly
            rather than loading it
            (if the first non-whitespace character is not
            '<' will decode as plain text)

        NOTE: if data and source are given, will not load source,
        but will treat data like it came from source
        """
        self.clean()
        self._lineStarts=[] # type: ignore
        self._html=""
        isHtml=False
        if data is not None:
            if source is not None and not hasattr(source,'read'):
                self._url=Url(source)
            data=data.strip()
            if data and data[0]=='<':
                isHtml=True
        elif hasattr(source,'html'):
            # looks like we're wrapping it
            self._wrapped=source
            self._url=None
            data=self._wrapped.html
            isHtml=True
        elif hasattr(source,'text'):
            # looks like we're wrapping it
            self._wrapped=source
            self._url=None
            data=self._wrapped.html
        elif source is not None:
            f=open(source,'rb')
            self._url=Url(source)
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
            from htmlTools import txt2html
            data=txt2html(data)
        self._html=data

    def save(self, # pylint: disable=arguments-differ
        asFilename:typing.Optional[UrlCompatible]=None
        )->bool:
        """
        asFilename can be:
            * None to save over existing
            * an html filename
            * any file type a wrapped object supports
            * a file-like object (if non-wrapped)
            * "-" for stdout (if non-wrapped)
        """
        if asFilename is not None:
            if isinstance(asFilename,str) and asFilename=='-':
                print(self.html)
                return True
            asFilename=asUrl(asFilename)
        if asFilename is None \
            or asFilename.ext not in ('htm','html','xhtml'):
            #
            if self._wrapped is not None and hasattr(self._wrapped,'filename'):
                return self._wrapped.filename.save(asFilename)
        if asFilename is None:
            if self.filename is not None:
                asFilename=self.filename
            else:
                asFilename=self.DefaultFilename
        asFilename.writeString(self.html)
        return True

    @property
    def url(self)->typing.Optional[Url]:
        """
        :return: where this document came from,or None if there isn't one

        NOTE: unlike Html.url,assigning only relabels the document;
            it does not clear or reload the content
        """
        if self._wrapped is not None and hasattr(self._wrapped,'filename'):
            return asUrl(self._wrapped.filename)
        return self._url
    @url.setter
    def url(self,url:typing.Optional[UrlCompatible]):
        self._url=None if url is None else Url(url)
    @property
    def filename(self)->typing.Optional[Url]:
        """
        :return: where this document came from,or None if there isn't one

        NOTE: unlike Html.url,assigning only relabels the document;
            it does not clear or reload the content
        """
        return self.url
    @filename.setter
    def filename(self,url:typing.Optional[UrlCompatible]): # type: ignore
        self.url=url

    @property
    def html(self)->str:
        """
        get the document as html
        """
        if not self._html:
            return ''
        return self._html
    @html.setter
    def html(self,html:typing.Any):
        if not isinstance(html,str):
            html=Html(html).html # let htmlTools coerce urls, files, bytes, ...
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
            ret:typing.List[str]=[]
            i=1
            for c in self.chapters:
                title=c.title
                if title is None or not title: # type: ignore
                    title='Chapter '+str(i)
                ret.append(title)
                ret.append(len(title)*'-')
                #ret.append(c.text)
                ret.append('')
                i+=1
            self._text='\n'.join(ret)
        return self._text
    @text.setter
    def text(self,text:PlaintextCompatible):
        super(Html).text=text # type: ignore

    def _chapterSplit(self,
        element:"EtreeElement",
        headingLevel:str='h1'
        )->typing.Iterable[typing.Tuple[
            "EtreeElement",typing.Iterable["EtreeElement"]]]:
        """
        Helper function to split a document into chapters when formatted like:
            <h2>chapter title</h2>
            chapter contents
            <h2>next chapter title</h2>
            ...

        It is designed such that someday you can have different heading levels
            for an engineering style document

        :param element: the starting xml element
        :param headingLevel: the level we are operating at
        """
        ret:typing.List[typing.Tuple[
            EtreeElement,typing.List[EtreeElement]]]=[]
        nodes=self.etree.xpath(f'//*/{headingLevel}')
        for i,titleNode in enumerate(nodes):
            #print('FOUND',titleNode.text)
            xpath=f'/html/body/{headingLevel}[{i+1}]'
            xpath=f'{xpath}/following-sibling::node()[not(self::{headingLevel})]' # noqa: E501
            xpath=f'{xpath}[count(preceding-sibling::{headingLevel})={i+1}]'
            contentNodes=element.xpath(xpath) # type: ignore
            contentNodes=typing.cast(typing.List["EtreeElement"],contentNodes)
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
                return ''
            for el in xml.xpath("//meta[contains(@name,'Author')]"):
                self._author=el.attrib['content']
            if self._title is None and self.filename is not None:
                # attempt to get it from the filename
                x=self.filename.name.split('.',1)[0].split('-',1)
                if len(x)>1:
                    x=x[1].replace('_',' ').strip()
                    if x:
                        self._title=x
        if self._author is None:
            return ''
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
                return ''
            for el in xml.xpath("//title"):
                self._title=el.text
            if self._title is None and self.filename is not None:
                # attempt to get it from the filename
                x=str(self.filename).rsplit(os.sep,1)[-1].split('.',1)[0]
                x=x.split('-',1)[0].replace('_',' ').strip()
                if x:
                    self._title=x
        if self._title is None:
            return ''
        return self._title
    @title.setter
    def title(self,value:str): # type: ignore
        self._title=value
        # TODO: save to file and mark dirty

    @property
    def children(self # type: ignore
        )->typing.Iterable[HtmlChapter]:
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
        self._children=[HtmlChapter(self,c) for c in children]

    @property
    def comments(self)->typing.Iterable[Comment]:
        """
        get all comments
        """
        if self._comments is None:
            from .comment import Comment
            self._comments=[]
            for comment in self.etree.xpath('//*/comment()'):
                _,_,_,position=self._findLocation(comment)
                comment=Comment(self.doc,self,position)
                self._comments.append(comment)
        return self._comments

    def commentsInRange(self,
        position:typing.Tuple[int,int]
        )->typing.Iterable[Comment]:
        """
        get all comments within a prescribed range

        :param position: an array or tuple like (start,end)
        """
        found:typing.List[Comment]=[]
        print(position)
        for comment in self.comments:
            if comment.position[0]>=position[0] \
                and comment.position[1]<=position[1]:
                #
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
                    if htmlDocument is None:
                        print('ERR: no document loaded yet')
                    else:
                        print('Chapters:')
                        for c in htmlDocument.chapters:
                            print('  ',c.title)
                elif arg[0]=='--json':
                    if htmlDocument is None:
                        print('ERR: no document loaded yet')
                    else:
                        print(htmlDocument.json)
                elif arg[0]=='--text':
                    if htmlDocument is None:
                        print('ERR: no document loaded yet')
                    else:
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
        print('  --json .......... dump a json representation of the doc\'s structure') # noqa: E501
        print('  --text .......... dump a plaintext representation of the doc')
        return -1
    return 0

if __name__=='__main__':
    import sys
    sys.exit(cmdline(sys.argv[1:]))
