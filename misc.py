#!/usr/bin/env
# -*- coding: utf-8 -*-
"""
Miscelaneous functions
"""
import typing
if typing.TYPE_CHECKING:
    from docStructure.document import Document


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

def stringToSlice(s:str)->typing.Union[int,slice]:
    """
    Convert a string representation of a slice or index
    into an actual slice or integer.

    :param s: the string to convert
    :return: an integer or a slice object
    """
    parts=s\
        .replace('...','..')\
        .replace(',','..')\
        .replace('--','..')\
        .replace('-','..')\
        .split('..')
    if len(parts)>1:
        index=slice(int(parts[0]),int(parts[1]))
    else:
        index=int(parts[0])
    return index

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
        import manuskriptFormat # type: ignore # pylint: disable=import-error
        doc=manuskriptFormat.Manuskript(filename) # type: ignore
        doc=typing.cast("Document",doc)
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
