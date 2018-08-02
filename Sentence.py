import nltk
from Location import *
from Word import *
from DocFrag import *

		
class Sentence(DocFrag):
	def __init__(self,doc,parent):#(self,value,doc=None,line=0,position=0):
		#location.__init__(self,doc,line,position)
		#self.__eq__(value)
		#self.words=' '.split(value)
		#for i in range(self.words):
		#	self.words[i]=Word(self.words[i],doc,line,position)
		#	position=position+len(word)+1 # TODO: This could be better
		DocFrag.__init__(self,doc,parent)
		
	def set(self,location,text):
		self.location=location
		self.children=[]
		# TODO: this tokenizer does not work well.
		#	see: https://github.com/armatthews/TokenizeAnything
		words=nltk.word_tokenize(text)
		locs=findTokenLocations(text,words,self.location[0])
		# TODO: this tokenizer doesn't work well either
		# looking into BLLIP, but this bug:
		#	https://github.com/BLLIP/bllip-parser/issues/48
		partsOfSpeech=nltk.pos_tag(words) # where tokens is [(word,part_of_speech)]
		for i in range(len(partsOfSpeech)):
			p=partsOfSpeech[i]
			w=Word(self.doc,self)
			w.set(locs[i],p[0],p[1])
			self.children.append(w)
			
	def sentenceNum(self):
		"""
		sentence number within paragraph
		"""
		return self.parent.sentences.index(self)
		
	def paragraphNum(self):
		"""
		para number within chapter
		"""
		return self.parent.paragraphNum()
		
	def chapterNum(self):
		"""
		chapter number within document
		"""
		return self.parent.parent.chapterNum()
			
	def structure(self):
		if True:
			rd_parser=nltk.RecursiveDescentParser(grammar1)
			for tree in rd_parser.parse([w.word for w in self.children]):
				print(tree)
		else:
			from nltk.data import find
			model_dir = find('models/bllip_wsj_no_aux').path
			print('Loading BLLIP Parsing models...')
			bllip = BllipParser(model_dir)
			print('Done.')
			tree=bllip.parse_one([w.word for w in self.children])
			print tree
	
	@property
	def words(self):
		"""
		get all words related to this frag
		"""
		return self.children
		
	@property
	def sentences(self):
		"""
		get all sentences related to this frag
		(be it a parent sentence or child sentences)
		"""
		return [self]
		
	@property
	def paragraphs(self):
		"""
		get all sentences related to this frag
		(be it a parent paragraph or child paragraphs)
		"""
		return [self.parent]
		
	@property
	def chapters(self):
		"""
		get all chapters related to this frag
		(be it a parent paragraph or child chapters)
		"""
		return [self.parent.parent]
