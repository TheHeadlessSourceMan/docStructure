#!/usr/bin/env
# -*- coding: utf-8 -*-
"""
This example finds the most often used words in the doc
"""


def cmdline(args):
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
                pd=ParsedDocument(arg)
                usage=pd.getWordUsage()
                print(arg)
                print("There are",pd.totalWordCount(),'total words in this doc,',pd.uniqueWordCount(),'unique')
                print("The top ten most frequent words in this doc:")
                for i in range(10):
                    print('\t',usage[i][0],usage[i][1])
                    if printhelp:
                        print('Usage:')
                        print('  mostFrequent.py [options]')
                        print('Options:')
                        print('   NONE')


if __name__=='__main__':
    import sys
    cmdline(sys.argv[1:])
