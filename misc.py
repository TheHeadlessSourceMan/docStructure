#!/usr/bin/env
# -*- coding: utf-8 -*-
"""
Miscelaneous functions
"""
import typing
import re


NLTK_PARTS_OF_SPEECH: typing.Dict[str, typing.Tuple[str,str]]=\
    { # abbreviation:(family,name)
    'CC':('conjunction','Coordinating conjunction'),
    'CD':('cardinal number','Cardinal number'),
    'DT':('determiner','Determiner'),
    'EX':('existential there','Existential there'),
    'FW':('foreign word','Foreign word'),
    'IN':('conjunction','Preposition or subordinating conjunction'),
    'JJ':('adjective','Adjective'),
    'JJR':('adjective','Adjective,comparative'),
    'JJS':('adjective','Adjective,superlative'),
    'LS':('list item marker','List item marker'),
    'MD':('modal','Modal'),
    'NN':('noun','Noun,singular or mass'),
    'NNS':('noun','Noun,plural'),
    'NNP':('noun','Proper noun,singular'),
    'NNPS':('noun','Proper noun,plural'),
    'PDT':('predeterminer','Predeterminer'),
    'POS':('possessive ending','Possessive ending'),
    'PRP':('pronoun','Personal pronoun'),
    'PRP$':('pronoun','Possessive pronoun'),
    'RB':('adverb','Adverb'),
    'RBR':('adverb','Adverb,comparative'),
    'RBS':('adverb','Adverb,superlative'),
    'RP':('particle','Particle'),
    'SYM':('symbol','Symbol'),
    'TO':('to','to'),
    'UH':('interjection','Interjection'),
    'VB':('verb','Verb,base form'),
    'VBD':('verb','Verb,past tense'),
    'VBG':('verb','Verb,gerund or present participle'),
    'VBN':('verb','Verb,past participle'),
    'VBP':('verb','Verb,non-3rd person singular present'),
    'VBZ':('verb','Verb,3rd person singular present'),
    'WDT':('determiner','Wh-determiner'),
    'WP':('pronoun',''),
    'WP$':('pronoun','Possessive wh-pronoun'),
    'WRB':('adverb','Wh-adverb')
    }

@typing.overload
def html2txt(html:None)->None:
    ...
@typing.overload
def html2txt(html:str)->str:
    ...
def txt2html(
    txtLine:typing.Optional[str],
    symbolicFormatting:bool=True,
    createLinks:bool=True,
    hLevel:int=2
    )->typing.Optional[str]:
    """
    Symbolic formatting:
        _txt_=> <u>txt</u>
        *txt*=> <b>txt</b>
        /txt/=> <i>txt</i>
        txt:=> <h2>txt<h2>
        * txt=> <li>txt</li>
        ---------=> <hr />
    """
    if txtLine is None:
        return None
    hLevel=str(hLevel)
    txtLine=txtLine.replace('&','&amp;')
    txtLine=txtLine.replace('  ',' &nbsp;')
    txtLine=txtLine.replace('<','&lt;')
    txtLine=txtLine.replace('>','&gt;')
    if symbolicFormatting:
        seps=['-','=','\\*','/','#','\\~','x','X']
        txtLine=re.sub(r"""_([^\s][^_]*)_""","""<u>\1</u>""",txtLine)
        txtLine=re.sub(r"""\*([^\s][^_]*)\*""","""<b>\1</b>""",txtLine)
        txtLine=re.sub(r"""/([^\s][^_]*)/""","""<i>\1</i>""",txtLine)
        txtLine=re.sub(r"""^\s*\*\s([^^]*)""","""<li>\1</li>""",txtLine)
        txtLine=re.sub(r"""([^:]*):\s*\Z""",
            """<h"""+hLevel+""">\1</h"""+hLevel+""">""",txtLine)
        for sep in seps:
            txtLine=re.sub(r"""\s*["""+sep+r"""]{2,9999}\s*""",
                """<hr />""",txtLine)
    if createLinks:
        txtLine=re.sub(
            r"""((?:file)|(?:http)|(?:ftp)|(?:https)|(?:mailto)|(?:sftp)://[^\s]*)""",
            r"""<a href="\1">\1</a>""",txtLine)
        txtLine=re.sub(
            r"""(?:\s|^)([^\s]+?@[^\s]+?\.[^\s]{2,4})""",
            r"""<a href="mailto://\1">\1</a>""",txtLine)
    return txtLine #txtLine.splitlines()[0]

@typing.overload
def html2txt(html:None)->None:
    ...
@typing.overload
def html2txt(html:str)->str:
    ...
def html2txt(html:typing.Optional[str])->typing.Optional[str]:
    """
    convert html to plain text

    :param html: html to convert
    :return: plain text

    Capable of using (in order):
        BeautifulSoup
        nltk (old)
        brute force text matching (not perfect)
            does not handle special chars like &u1234;
            ignores <pre>
    """
    if html is None:
        return None
    if hasattr(html,'text'):
        return html.text
    try:
        from bs4 import BeautifulSoup
        soup=BeautifulSoup(html)
        # kill all script and style elements
        for script in soup(["script","style"]):
            script.extract()    # rip it out
        # get text
        text=soup.get_text()
        # break into lines and remove leading and trailing space on each
        lines=(line.strip() for line in text.splitlines())
        # break multi-headlines into a line each
        chunks=(phrase.strip() for line in lines for phrase in line.split("  "))
        # drop blank lines
        return '\n'.join(chunk for chunk in chunks if chunk)
    except ImportError:
        pass
    try:
        import nltk
        return nltk.clean_html(html)
    except Exception:
        pass
    replacements=[
        ('  ',' '),
        ('  ',' '),
        ('&nbsp;',' '),
        ('&gt;','>'),
        ('&lt;','<'),
        ('&amp;',' ')
        ]
    ret:typing.List[str]=[]
    first=True
    ready=False
    html=html.replace('\n','').replace('\r','').replace('<br>','\n')
    html=html.replace('<br />','\n').replace('<br/>','\n')
    for h in html.split('<'):
        #print(h)
        if first:
            if ready:
                ret.append(h[0])
            first=False
        elif ready:
            ret.append(h.rsplit('>',1)[-1])
        elif len(h)>1 and h[1].startswith('body'):
            ready=True
    retStr=' '.join(ret)
    for this,that in replacements:
        retStr=retStr.replace(this,that)
    return retStr

@typing.overload
def fixTitle(title:None)->None:
    ...
@typing.overload
def fixTitle(title:str)->str:
    ...
def fixTitle(title:typing.Optional[str])->typing.Optional[str]:
    """
    fix a title to conform to proper grammar

    for instance "the man in the iron mask" -> "The Man in the Iron Mask"

    :param title: the title to fix up
    """
    if title is None:
        return title
    # technically ANY preposition,but that's a little too big for
    # a simple python list
    prepositions=['for','of','to','the','in','and','or','nor','but','a','an',
        'yet','so','at','around','by','after','along','from','on',
        'with','without']
    result: typing.List[str]=[]
    first=True
    for element in title.replace('_',' ').split():
        if first and element in prepositions:
            first=False
            result.append(element)
        else:
            if len(element)>1:
                result.append(element[0].upper()+element[1:])
            else:
                result.append(element.upper())
    return ' '.join(result)


def load(filename:str,ext:typing.Optional[str]=None)->typing.Any:
    """
    quickie to load a file and return the results

    :property ext: file extension of the type to load

    TODO: only works with html and manuskript
    need to add calibre and libreoffice and stuff
    """
    if ext is None:
        ext=filename.rsplit('.',1)[-1]
    elif ext.startswith('.'):
        ext=ext[1:]
    if ext in ['msk']:
        import manuskriptFormat
        doc=manuskriptFormat.Manuskript(filename)
    else:
        import docStructure.htmlDocument
        doc=docStructure.htmlDocument.HtmlDocument(filename)
    return doc


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
        print('  misc.py [options]')
        print('Options:')
        print('   NONE')
        return -1
    return 0


if __name__=='__main__':
    import sys
    sys.exit(cmdline(sys.argv[1:]))
