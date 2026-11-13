#!/usr/bin/env
# -*- coding: utf-8 -*-
"""
A single section in the document hierarchy tree
"""
import typing
from htmlTools import HtmlCompatible
from .docFrag import DocFrag
if typing.TYPE_CHECKING:
    from docStructure import Document, Chapter


class Section(DocFrag):
    """
    A single section in the document hierarchy tree

    TODO: currently a work in progress
    """

    frag='section'

    def __init__(self,doc:"Document",parent:DocFrag,position:int):
        DocFrag.__init__(self,doc,parent,position)
        self._children:typing.List[typing.Union["Chapter","Section"]]=[]
        self._name:typing.Optional[str]=None

    @property
    def level(self)->int:
        """
        What section level we are at
        """
        if hasattr(self.parent,'level'):
            return self.parent.level+1
        return 1

    @property
    def name(self)->str:
        """
        the name of this section
        """
        if self._name is None:
            self._name=''
        return self._name
    @name.setter
    def name(self,name:str):
        self._name=name
    title=name

    def tree(self,indent:str)->str:
        """
        the item tree
        """
        ret:typing.List[str]=[self.name]
        for c in self.children:
            if hasattr(c,'tree'):
                ret.append(c.tree(indent+'  '))
        return ('\n'+indent).join(ret)

    def flat(self)->typing.Iterable["DocFrag"]:
        """
        the section,flattened
        """
        ret:typing.List["DocFrag"]=[]
        for c in self.children:
            if isinstance(c,Section):
                ret.extend(c.flat())
            else:
                ret.append(c)
        return ret

    @property
    def html(self)->str:
        """
        The section in html form
        """
        ret:typing.List[str]=[]
        if self.parent._showDocStructureInHtml: # pylint: disable=protected-access # noqa: E501
            ret.append('<!-- BEGIN SECTION '+self.title+' -->')
        if self.compile in ('2',True):
            level=self.level-self.parent._minLevel
            # print('HTML conversion at',self.label,level,self.title)
            if level>1 and int(self.label)>=3:
                level=str(level)
                ret.append('<h'+level+'>'+self.title+'</h'+level+'>')
            children=self.children
            for c in children:
                html=c.html
                if html:
                    if isinstance(html,property):
                        html=html.fget(c)
                    ret.append(html)
        else:
            print('SKIPPING:',self.compile,self._filename)
        if self.parent._showDocStructureInHtml: # pylint: disable=protected-access # noqa: E501
            ret.append('<!-- END SECTION '+self._filename+' -->')
        ret='\n'.join(ret)
        return ret
    @html.setter
    def html(self,html:HtmlCompatible): # type: ignore
        self.contents=html

    @property
    def text(self)->str: # type: ignore
        """
        The section in plain text form
        """
        ret:typing.List[str]=[]
        if self.compile in ('2',True):
            if self.label=='3':
                ret.append(self.title)
                ret.append('='*len(self.title))
                ret.append('')
            for c in self.children:
                ret.append(c.text)
        else:
            print('SKIPPING:',self.compile,self._filename)
        return '\n'.join(ret)
    @text.setter
    def text(self,text:HtmlCompatible): # type: ignore
        self.contents=text


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
                if arg[0] in ['-h','--help']:
                    printhelp=True
                else:
                    print('ERR: unknown argument "'+arg[0]+'"')
            else:
                print('ERR: unknown argument "'+arg+'"')
    if printhelp:
        print('Usage:')
        print('  section.py [options]')
        print('Options:')
        print('   NONE')
        return -1
    return 0


if __name__=='__main__':
    import sys
    sys.exit(cmdline(sys.argv[1:]))
