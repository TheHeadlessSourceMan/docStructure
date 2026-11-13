"""
Utils and wrappers for dealing with words, grammar, parts of speech...
all that English class rigamaroll.
"""
import typing
import nltk
if typing.TYPE_CHECKING:
    from nltk.stem import WordNetLemmatizer


PartsOfSpeechDict=typing.Dict[str,typing.Tuple[str,str]]
NLTK_PARTS_OF_SPEECH:PartsOfSpeechDict={ # abbreviation:(family,name)
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
PARTS_OF_SPEECH=NLTK_PARTS_OF_SPEECH

def wordsToPartsOfSpeech(
    words:typing.List[str]
    )->typing.List[typing.Tuple[str,str]]:
    """
    get the part of speech for each word

    :param words: list of words
    :return: list of tuples (word, part_of_speech)
    """
    # TODO: this tokenizer doesn't work well
    # looking into BLLIP,but this bug:
    #    https://github.com/BLLIP/bllip-parser/issues/48
    return nltk.pos_tag(words) # where tokens is [(word,part_of_speech)]


GrammarTreeNode=typing.List[typing.Union[str,"GrammarTreeNode"]]
def sentenceStructure(sentence:str)->GrammarTreeNode:
    """
    Get the grammatical structure tree of a sentence
    """
    ret:GrammarTreeNode=[]
    if True:
        rd_parser=nltk.RecursiveDescentParser(nltk.grammar)
        for tree in rd_parser.parse(sentence.split()):
            ret.append(tree)
    else:
        from nltk.data import find
        model_dir=find('models/bllip_wsj_no_aux').path
        ret.append('Loading BLLIP Parsing models...')
        from bllipparser import BllipParser
        bllip=BllipParser(model_dir)
        ret.append('Done.')
        tree=bllip.parse_one(sentence.split())
        ret.append(tree)
    return ret


def splitIntoSentences(text:str)->typing.List[str]:
    """
    Split the given text into sentences using NLTK.

    :param text: the text to split
    :return: list of sentences
    """
    return nltk.sent_tokenize(text)


_LEMMATIZER:typing.Optional["WordNetLemmatizer"]=None
def wordRoot(text:str)->str:
    """
    get the undecorated version of a word:
        cat=> cat
        cats=> cat
        run=> run
        ran=> run
        running=> run
    see:
        http://www.nltk.org/api/nltk.stem.html
    """
    global _LEMMATIZER
    if _LEMMATIZER is None:
        from nltk.stem import WordNetLemmatizer
        _LEMMATIZER=WordNetLemmatizer()
    return _LEMMATIZER.lemmatize(text)


def getDictionaryDefinitions(word:str)->typing.List[str]:
    """
    Get dictionary definitions for the given word.

    :param word: the word to look up
    :return: list of definitions
    """
    import Dictionary
    return Dictionary.getDefinitions(word)


_globalReferenceDictionary=None # there will be only one instance
def referenceDictonary()->typing.Dict[str,str]:
    """
    :return: the reference dictionary
        (will be automatically loaded as necessary)
    """
    global _globalReferenceDictionary
    if _globalReferenceDictionary is None:
        print('Loading dictionary...')
        from nltk.corpus import cmudict
        _globalReferenceDictionary=cmudict.dict()
    return _globalReferenceDictionary


def chapterTokenize(doc:str)->typing.List[str]:
    """
    Split the given document into chapters using NLTK.

    :param doc: the document to split
    :return: list of chapters
    """
    return nltk.chap_tokenize(doc)


def findTokenLocations(
    text:str,
    words:typing.Iterable[str],
    plusOffs:int=0
    )->typing.Iterable[typing.Tuple[int,int]]:
    """
    :param text: the original text
    :param words: words tokenized from the text (if None,will do it ourselves)
    :param plusOffs: add this to every value

    returns [(start,end)] for all words
    """
    if words is None:
        words=nltk.wordpunct_tokenize(text)
    e=0
    ret:typing.List[typing.Tuple[int,int]]=[]
    for w in words:
        s=text.find(w,e)
        e=s+len(w)
        ret.append((s+plusOffs,e+plusOffs))
    return ret


def wordTokenize(text:str)->typing.List[str]:
    """
    Tokenize the given text into words using NLTK.

    :param text: the text to tokenize
    :return: list of words
    """
    # TODO: this tokenizer does not work well.
    #    see: https://github.com/armatthews/TokenizeAnything
    return nltk.word_tokenize(text)


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
