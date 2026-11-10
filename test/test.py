#!/usr/bin/env
# -*- coding: utf-8 -*-
"""
Run unit tests

See:
    http://pyunit.sourceforge.net/pyunit.html
"""
import unittest
import os
import shutil
from docStructure import *



__HERE__=os.path.abspath(__file__).rsplit(os.sep,1)[0]+os.sep
results_dir=__HERE__+'results'+os.sep
class HtmlDocumentTests(unittest.TestCase):
    """
    Run unit test
    """

    def setUp(self):
        os.chdir(__HERE__)
        try:
            shutil.rmtree(results_dir)
        except:
            pass
        os.mkdir(results_dir)
        self.filename=__HERE__+'test1.html'

    def tearDown(self):
        pass# shutil.rmtree(results_dir)

    def listChapters(self):
        msk=HtmlDocument(self.filename)
        contents=msk.chapters
        print('listChapters')
        print(contents)# TODO: match against known table
        
    def toHtml(self):
        msk=HtmlDocument(self.filename)
        contents=msk.html
        print('toHtml')
        print(contents)# TODO: match against known table
        
    def toText(self):
        msk=HtmlDocument(self.filename)
        contents=msk.text
        print('toText')
        print(contents)# TODO: match against known table
        
    def title(self):
        msk=HtmlDocument(self.filename)
        contents=msk.title
        print('title')
        print(contents)# TODO: match against known table
        

def suite(tests=None):
    """
    Combine unit tests into an entire suite
    """
    testSuite = unittest.TestSuite()
    testSuite.addTest(HtmlDocumentTests("listChapters"))
    testSuite.addTest(HtmlDocumentTests("toHtml"))
    #testSuite.addTest(HtmlDocumentTests("toText"))
    testSuite.addTest(HtmlDocumentTests("title"))
    return testSuite


def run(tests=None,output=None,verbosity=2,failfast=False):
    """
    run the test suite
    """
    if output is None:
        output=sys.stdout
    else:
        output=open(output,'wb')
    runner=unittest.TextTestRunner(output,verbosity=verbosity,failfast=failfast)
    runner.run(suite(tests))


def cmdline(args):
    """
    Run the command line

    :param args: command line arguments (WITHOUT the filename)
    """
    printhelp=False
    save=None
    tests=[]
    if not args:
        pass#printhelp=True
    else:
        for arg in args:
            if arg.startswith('-'):
                arg=[a.strip() for a in arg.split('=',1)]
                if arg[0] in ['-h','--help']:
                    printhelp=True
                elif arg[0]=='--save':
                    save=arg[1]
                else:
                    print('ERR: unknown argument "'+arg[0]+'"')
            else:
                tests.append(arg)
    if printhelp:
        print('Usage:')
        print('  test.py [options] [tests]')
        print('Options:')
        print('   --save=filename ............... save the test output to this file, rather than the console')
    else:
        run(tests,save)


if __name__=='__main__':
    import sys
    cmdline(sys.argv[1:])
