#!/usr/bin/env
# -*- coding: utf-8 -*-
"""
This program detects frequent words within all sentences
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
                print(argusage=pd.closestProximityOfWords())
                print("The top ten closest recurring words in this doc:")
                for i in range(10):
                    sentence=pd.doc[usage[i][1].valueStart-20:usage[i][2].valueEnd+20]
                    sentence=sentence.replace('\n',' ')
                    print('\t',usage[i][0],'"'+usage[i][1].value()+'"','in',sentence)
    if printhelp:
        print('Usage:')
        print('  frequentSentence.py [options]')
        print('Options:')
        print('   NONE')


if __name__=='__main__':
    import sys
    cmdline(sys.argv[1:])
