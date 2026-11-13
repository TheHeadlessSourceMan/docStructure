#!/usr/bin/env
# -*- coding: utf-8 -*-
"""
Tools to perform advanced searching within a document
"""
import typing
import re
from docStructure import Document,Word
from .wordUtils import PARTS_OF_SPEECH


# shorthand examples:
#    [s]?he          =any regex works for words
#    he ran          =words are separated by spaces
#    he|she [~VBD]   =pos verb,past tense
#    he|she [~~verb] =anything in the verb pos family
#    he|she [~VB.*]  =regex is fine in pos and pos families
#    he did(n't|\ not)=escape spaces (though \s+ is probably better)
SHORTHAND_REGEX=re.compile(
    r"""(?:\[~(?:~([^\]]*))|([^\]]*)\])?(\\\s|[^\s]+)?\s""",re.DOTALL)


def allPosInFamily(families:typing.Iterable[str])->typing.Iterable[str]:
    """
    families can be array if you want to get more than one
    """
    res:typing.List[str]=[]
    if not isinstance(families,list):
        families=[families]
    for k,v in list(PARTS_OF_SPEECH.items()):
        if v[0] in families:
            res.append(k)
    return res

def posReFind(
    regex:typing.Union[typing.Pattern[str],str]
    )->typing.Iterable[str]:
    """
    find all parts of speech matching regex
    """
    ret:typing.List[str]=[]
    if isinstance(regex,str):
        regex=re.compile(regex)
    for k in list(PARTS_OF_SPEECH.keys()):
        if regex.match(k):
            ret.append(k)
    return ret

def posFamilyReFind(
    regex:typing.Union[str,typing.Iterable[str]]
    )->typing.Iterable[str]:
    """
    find all parts of speech families matching regex
    """
    ret:typing.List[str]=[]
    if isinstance(regex,str):
        regex=re.compile(regex)
    for v in list(PARTS_OF_SPEECH.values()):
        if regex.match(v[0]):
            ret.append(v[0])
    return ret


class Matcher:
    """
    Tool to perform a complex match on a document
    """

    def __init__(self,
        regex:typing.Optional[typing.Union[str,typing.Iterable[str]]]=None,
        partsOfSpeech:typing.Optional[typing.Iterable[str]]=None,
        partsOfSpeechFamilies:typing.Optional[str]=None,
        invert:bool=False):
        """
        partsOfSpeech - can be a single item or a list
        partsOfSpeechFamilies - can be a single item or a list
        """
        if isinstance(regex,str):
            regex=re.compile(regex,re.DOTALL|re.IGNORECASE)
        self.regex=regex
        if partsOfSpeech is None:
            self.partsOfSpeech=[]
        elif not hasattr(partsOfSpeech,'__iter__') \
            or isinstance(partsOfSpeech,str):
            self.partsOfSpeech=list(partsOfSpeech)
        else:
            self.partsOfSpeech=partsOfSpeech
        if partsOfSpeechFamilies is not None:
            if self.partsOfSpeech is None:
                self.partsOfSpeech=[allPosInFamily(partsOfSpeechFamilies)]
            else:
                self.partsOfSpeech.extend(
                    allPosInFamily(partsOfSpeechFamilies))
        self.invert:bool=invert

    def match(self,word:Word):
        r"""
        NOTE: even though we pass in a word the re can match the whole doc
        afterward, for instance,United\s+States(\s+of\s+America)?

        NOTE: this also means that you may want to end your re with \s+
            because "catapult" will return true for the re "cat"
        """
        result=True
        if self.partsOfSpeech and word.partOfSpeech not in self.partsOfSpeech:
            #print('"'+str(word)+'"','failed pos'+str(self.partsOfSpeech))
            result=False
        #if self.regex is not None and not self.regex.match(
        #   word.doc.text,word.location[0]):
        if self.regex is not None and not self.regex.match(str(word)):
            #print('"'+str(word)+'" failed regex "'+str(self.regex)+'"')
            result=False
        if self.invert:
            result=result is False
        return result

    def __repr__(self)->str:
        """
        get a string representation of this object
        """
        ret:typing.List[str]=[]
        if self.regex is None:
            ret.append(str(self.regex))
        if self.partsOfSpeech is not None:
            ret.extend(self.partsOfSpeech)
        return ' '.join(ret)

MatcherCompatible=typing.Union[
    Matcher,
    str,
    typing.Pattern[str],
    typing.Iterable[Matcher,str,typing.Pattern[str]]]


class MatcherSequence:
    """
    a sequence of matchers
    """

    def __init__(self,
        matchers:typing.Optional[MatcherCompatible]=None
        ):
        """
        :param matchers: _description_, defaults to None
        """
        self.matchers:typing.List[Matcher]=[]
        self.extend(matchers)

    def append(self,
        matcher:typing.Optional[MatcherCompatible]
        )->None:
        """
        matcher can be:
        a) a matcher class
        b) a shorthand string
        c) a regular expression
        c) an array of any of this
        """
        if matcher is None:
            pass
        elif isinstance(matcher,list):
            for m in matcher:
                self.append(m)
        elif isinstance(matcher,str):
            for m in SHORTHAND_REGEX.finditer(matcher+' '):
                pos=None
                posFam=None
                regex=None
                invert=False
                if m.group(1) is not None:
                    posFam=posFamilyReFind(m.group(1))
                if m.group(2) is not None:
                    pos=posReFind(m.group(2))
                if m.group(3) is not None:
                    regex=re.compile(m.group(3))
                #print(regex,pos,posFam,invert)
                self.append(Matcher(regex,pos,posFam,invert))
        #elif isinstance(matcher,re.Regex):
        #    self.matchers.append(Matcher(matcher))
        elif isinstance(matcher,Matcher):
            self.matchers.append(matcher)

    def extend(self,
        matchers:typing.Optional[MatcherCompatible]
        )->None:
        """
        really does the same thing as append().

        only here for the array list purists
        """
        self.append(matchers)

    def finditer(self,
        doc:typing.Union[str,Document]
        )->typing.Iterable[typing.List[Word]]:
        """
        doc can be a Document object or a plain text to convert into one

        each iteration is an array of words

        HINT: if you would rather have a (start,end) doc range,do
        (result[0].location[0],result[-1].location[-1])
        """
        if isinstance(doc,str):
            doc=Document(doc)
        words=doc.words()
        endi=len(words)-len(self.matchers)+1
        for i in range(endi):
            matched=[]
            for j in range(i,endi):
                for m in self.matchers:
                    if not m.match(words[j]):
                        matched=None
                        break
                    matched.append(words[j])
                if matched is None:
                    break
            if matched is not None:
                yield matched


def cmdline(args:typing.Iterable[str])->int:
    """
    Run the command line

    :param args: command line arguments (WITHOUT the filename)
    """
    sh=r""".*fathers"""
    _=args
    f=open('gettysberg.txt','rb')
    doc=f.read().decode('utf-8',errors='ignore')
    f.close()
    ms=MatcherSequence(sh)
    for m in ms.finditer(doc):
        print(' '.join([str(s) for s in m]))
    return 0


if __name__=='__main__':
    import sys
    sys.exit(cmdline(sys.argv[1:]))
