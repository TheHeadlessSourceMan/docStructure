import nltk
import re
import Document

NLTK_PARTS_OF_SPEECH={ # abbreviation:(family,name)
	'CC':('conjunction','Coordinating conjunction'),
	'CD':('cardinal number','Cardinal number'),
	'DT':('determiner','Determiner'),
	'EX':('existential there','Existential there'),
	'FW':('foreign word','Foreign word'),
	'IN':('conjunction','Preposition or subordinating conjunction'),
	'JJ':('adjective','Adjective'),
	'JJR':('adjective','Adjective, comparative'),
	'JJS':('adjective','Adjective, superlative'),
	'LS':('list item marker','List item marker'),
	'MD':('modal','Modal'),
	'NN':('noun','Noun, singular or mass'),
	'NNS':('noun','Noun, plural'),
	'NNP':('noun','Proper noun, singular'),
	'NNPS':('noun','Proper noun, plural'),
	'PDT':('predeterminer','Predeterminer'),
	'POS':('possessive ending','Possessive ending'),
	'PRP':('pronoun','Personal pronoun'),
	'PRP$':('pronoun','Possessive pronoun'),
	'RB':('adverb','Adverb'),
	'RBR':('adverb','Adverb, comparative'),
	'RBS':('adverb','Adverb, superlative'),
	'RP':('particle','Particle'),
	'SYM':('symbol','Symbol'),
	'TO':('to','to'),
	'UH':('interjection','Interjection'),
	'VB':('verb','Verb, base form'),
	'VBD':('verb','Verb, past tense'),
	'VBG':('verb','Verb, gerund or present participle'),
	'VBN':('verb','Verb, past participle'),
	'VBP':('verb','Verb, non-3rd person singular present'),
	'VBZ':('verb','Verb, 3rd person singular present'),
	'WDT':('determiner','Wh-determiner'),
	'WP':('pronoun'),
	'WP$':('pronoun','Possessive wh-pronoun'),
	'WRB':('adverb','Wh-adverb')
	}
	
# shorthand examples:
#	[s]?he           = any regex works for words
#	he ran           = words are separated by spaces
#	he|she [~VBD]    = pos verb, past tense
#	he|she [~~verb]  = anything in the verb pos family
#	he|she [~VB.*]   = regex is fine in pos and pos families
#	he did(n't|\ not)= escape spaces (though \s+ is probably better)
SHORTHAND_REGEX=re.compile(r"""(?:\[~(?:~([^\]]*))|([^\]]*)\])?(\\\s|[^\s]+)?\s""",re.DOTALL)

	
def allPosInFamily(families):
	"""
	families can be array if you want to get more than one
	"""
	res=[]
	if type(families)!=list:
		families=[families]
	for k,v in NLTK_PARTS_OF_SPEECH.items():
		if v[0] in families:
			res.append(k)
	return res
	
def posReFind(regex):
	"""
	find all parts of speech matching regex
	"""
	ret=[]
	if type(regex)==str or type(regex)==unicode:
		regex=re.compile(regex)
	for k in NLTK_PARTS_OF_SPEECH.keys():
		if regex.match(k):
			ret.append(k)
	return ret

def posFamilyReFind(regex):
	"""
	find all parts of speech families matching regex
	"""
	ret=[]
	if type(regex)==str or type(regex)==unicode:
		regex=re.compile(regex)
	for v in NLTK_PARTS_OF_SPEECH.values():
		if regex.match(v[0]):
			ret.append(v[0])
	return ret

class Matcher:
	def __init__(self,regex=None,partsOfSpeech=None,partsOfSpeechFamilies=None,invert=False):
		"""
		partsOfSpeech - can be a single item or a list
		partsOfSpeechFamilies - can be a single item or a list
		"""
		if type(regex)==str or type(regex)==unicode:
			regex=re.compile(regex,re.DOTALL|re.IGNORECASE)
		self.regex=regex
		if partsOfSpeech==None:
			self.partsOfSpeech=[]
		elif type(partsOfSpeech)!=list:
			self.partsOfSpeech=[partsOfSpeech]
		else:
			self.partsOfSpeech=partsOfSpeech
		if partsOfSpeechFamilies!=None:
			if self.partsOfSpeech==None:
				self.partsOfSpeech=[allPosInFamily(partsOfSpeechFamilies)]
			else:
				self.partsOfSpeech.extend(allPosInFamily(partsOfSpeechFamilies))
		self.invert=invert
		
	def match(self,word):
		"""
		NOTE: even though we pass in a word the re can match the whole doc afterward,
			for instance, United\s+States(\s+of\s+America)?
			
		NOTE: this also means that you may want to end your re with \s+
			because "catapult" will return true for the re "cat"
		"""
		result=True
		if len(self.partsOfSpeech)>0 and not word.partOfSpeech in self.partsOfSpeech:
			#print '"'+str(word)+'"','failed pos'+str(self.partsOfSpeech)
			result=False
		#if self.regex!=None and not self.regex.match(word.doc.text,word.location[0]):
		if self.regex!=None and not self.regex.match(str(word)):
			#print '"'+str(word)+'" failed regex "'+str(self.regex)+'"'
			result=False
		if self.invert:
			result=result==False
		return result
		
	def __str__(self):
		ret=[]
		if self.regex==None:
			ret.append(str(self.regex))
		if self.partsOfSpeech!=None:
			ret.extend(partsOfSpeech)
		return ' '.join(ret)
	
class MatcherSequence:
	def __init__(self,matchers=None):
		self.matchers=[]
		self.extend(matchers)
	
	def append(self,matcher):
		"""
		matcher can be:
		a) a matcher class
		b) a shorthand string
		c) a regular expression
		c) an array of any of this
		"""
		if matcher==None:
			pass
		elif type(matcher)==list:
			for m in matcher:
				self.append(m)
		elif type(matcher)==str or type(matcher)==unicode:
			for m in SHORTHAND_REGEX.finditer(sh+' '):
				pos=None
				posFam=None
				regex=None
				invert=False
				if m.group(1)!=None:
					posFam=posFamilyReFind(m.group(1))
				if m.group(2)!=None:
					pos=posReFind(m.group(2))
				if m.group(3)!=None:
					regex=re.compile(m.group(3))
				#print regex,pos,posFam,invert
				self.append(Matcher(regex,pos,posFam,invert))
		#elif type(matcher)==isinstance(matcher,re.Regex):
		#	self.matchers.append(Matcher(matcher))
		elif isinstance(matcher,Matcher):
			self.matchers.append(matcher)
	
	def extend(self,matchers):
		"""
		really does the same thing as append().
		
		only here for the array list purists
		"""
		self.append(matchers)
	
	def finditer(self,doc):
		"""
		doc can be a Document object or a plain text to convert into one
		
		each iteration is an array of words
		
		HINT: if you would rather have a (start,end) doc range, do 
		(result[0].location[0],result[-1].location[-1])
		"""
		if type(doc)==str or type(doc)==unicode:
			doc=Document.Document(doc)
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
				if matched==None:
					break
			if matched!=None:
				yield matched
	

sh=r""".*fathers"""
f=open('gettysberg.txt','r')
doc=f.read()
f.close()
ms=MatcherSequence(sh)
for m in ms.finditer(doc):
	print ' '.join([str(s) for s in m])