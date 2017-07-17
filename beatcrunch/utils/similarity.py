# Initial version by David Campion - 03/2017
# Adapted by Greg Fabre - avril to july 2017

import os, string, re, time
import operator

from unidecode import unidecode

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import linear_kernel
from nltk.stem.porter import PorterStemmer

import nltk
from nltk.corpus import stopwords #import stopwords from nltk corpus
from nltk.stem.snowball import FrenchStemmer #import the French stemming library
from nltk.stem.snowball import EnglishStemmer #import the English stemming library
from nltk.tokenize import TreebankWordTokenizer #import the Treebank tokenizer
from nltk.tokenize import WordPunctTokenizer
from nltk.tokenize import TreebankWordTokenizer
from nltk.tokenize import RegexpTokenizer
#from nltk.tokenize import ToktokTokenizer

from nltk.probability import FreqDist

#import lib to detect language
import utils.nltk_detect_lang as nltk_detect_lang
import utils.nltk_common as nltk_common

import utils.tok as tok

#name stemmers
stemmer_fr=FrenchStemmer()
stemmer_en=EnglishStemmer()

# Load tokenizer
# You can choose the most efficient, however wordpunct is working well
#tokenizer = TreebankWordTokenizer()
#tokenizer = WordPunctTokenizer()
#tokenizer = RegexpTokenizer(r'\w+')
#tokenizer = ToktokTokenizer()
tokenizer = tok.ToktokTokenizer()

# Get a sorted list of repetitive words
def freqDist(tokens):
    dist={}
    for t in tokens :
        if len(t) == 1 : continue

        if t in dist :
            dist[t] += 1
        else :
            dist[t] = 1

    out=[]
    for (k,v) in sorted(dist.items(), key=operator.itemgetter(1), reverse=True) :
        if v>1 : out.append(k)
        # if v==1 : dist.pop(k)

    return out

# stemer function text
def stem_tokens(tokens, stemmer):
    stemmed = []
    for item in tokens:
        stemmed.append(stemmer.stem(item))
    return stemmed

#tokenize a text depending on its language
def isInt(s):
    try:
        int(s)
        return True
    except ValueError:
        return False

def tokenizeText(text,lang):
    output =[]
    tokens = tokenizer.tokenize(text)
    plainwords = nltk_common.getPlainWords()

    lastToken=""
    for token in tokens :
        token = token.lower()
        # if lastToken :
        #     print("Test [{}]".format(lastToken+" "+token))
        # else :
        #     print("Test [{}]".format(token))

        if lastToken and lastToken+" "+token in plainwords :
            #print("Found [{}]".format(lastToken+" "+token))
            output.remove(lastToken)
            output.append(lastToken+" "+token)
            lastToken =""
        else :
            if len(token) == 1 :
                lastToken =""
                continue
            if token in nltk_common.getStopWords(lang) :
                lastToken =""
                continue
            if isInt(token) :
                lastToken =""
                continue

            output.append(token)
            lastToken = token

    return output

def stemTokens(t,lang) :
    if lang == "french" :
        return stem_tokens(t, stemmer_fr)
    elif lang == "english" :
        return stem_tokens(t, stemmer_en)
    else :
        return stem_tokens(t, stemmer_en)

def tokenize(text) :
    language = nltk_detect_lang.get_language(text)
    tokens = tokenizer.tokenize(text)
    #t = [token for token in tokens if token.lower() not in nltk_common.getStopWords(language) + nltk_common.punctuation]

    if language == "french" :
        return stem_tokens(tokens, stemmer_fr)
    elif language == "english" :
        return stem_tokens(tokens, stemmer_en)
    else :
        return stem_tokens(tokens, stemmer_en)

#------
#clean text: remove punctuation and get lower characters
def clean_text(text):
    lowers = text.lower()
    #code to remove punctuation. uncomment if required
    #table = {ord(char): None for char in string.punctuation}
    #cleaned = lowers.translate(table)
    cleaned = lowers
    return cleaned

def find_similar(token_dict, top_n = 1): #tfidf_matrix,

    # Only one item
    if len(token_dict) == 1 : return [[0,1,token_dict[0]]]

    # Reverse list to put the seed in first position
    reverse_dict=[]
    for n in range(0,len(token_dict)) :
        #print("Swap {} with {}".format(n,len(token_dict)-n-1))
        reverse_dict.append(token_dict[len(token_dict)-n-1])

    index = len(token_dict)-1

    tfidf = TfidfVectorizer(tokenizer=tokenize, stop_words=nltk_common.getStopWords("all"))
    #tfidf_matrix = tfidf.fit_transform(token_dict.values())
    tfidf_matrix = tfidf.fit_transform(reverse_dict)

    cosine_similarities = linear_kernel(tfidf_matrix[0:1], tfidf_matrix).flatten()

    related_docs_indices = [i for i in cosine_similarities.argsort()[::-1] if i != 0]

    #return top_n similar documents in the matrix. For each of them:
    # - index of the document in the matrix
    # - score of similarity
    # - text of the similar document.

    return [(index, cosine_similarities[index],reverse_dict[index]) for index in related_docs_indices][0:top_n]

# Tokenize text, remove common words, and sort tokens to get most used first
def findTags(text,lang,nb):
    tokens = tokenizeText(text,lang)
    return freqDist(tokens)[:nb]
