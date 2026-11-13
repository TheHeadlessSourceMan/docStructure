#!/usr/bin/env
# -*- coding: utf-8 -*-
"""
Miscelaneous functions
"""
import typing
if typing.TYPE_CHECKING:
    from docStructure.document import Document


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
