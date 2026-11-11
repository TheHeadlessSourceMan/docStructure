#!/usr/bin/env
# -*- coding: utf-8 -*-
"""
This class finds things for you
"""
import typing


class Finder:
    """
    This class finds things for you
    """

    def getAll(self,
        itemType:str,
        fileSeletionTree:str,
        useYield:bool=True
        )->typing.Union[typing.Generator[int,None,None],typing.Iterable[int]]:
        """
        Get all of a given type of item from a fileSeletionTree
        as a simple list
        """
        if useYield:
            # this does not work for some reason!
            for k,v in list(fileSeletionTree.children.items()):
                for i in v:
                    if k==itemType:
                        yield i
                    else:
                        yield from self.getAll(itemType,i,useYield)
        else:
            results=[]
            for k,v in list(fileSeletionTree.children.items()):
                for i in v:
                    if k==itemType:
                        if isinstance(i,list):
                            raise Exception
                        results.append(i)
                    else:
                        for r in self.getAll(itemType,i,useYield):
                            if isinstance(r,list):
                                raise Exception
                            results.append(r)
            return results


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
        print('  Finder.py [options]')
        print('Options:')
        print('   NONE')
        return -1
    return 0


if __name__=='__main__':
    import sys
    sys.exit(cmdline(sys.argv[1:]))
