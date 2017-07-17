import os,sys

import nltk
from nltk.corpus import stopwords #import stopwords from nltk corpus

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))

def getStopWords(lang) :
    if lang=="fr" or "french" in lang :
        swords = stopwords.words("french_custom")
    elif lang=="en" or "english" in lang :
        swords = stopwords.words("english_custom")
    else :
        swords = stopwords.words("french_custom") + stopwords.words("english_custom")
        # swords = getStopWords("french") + getStopWords("english") + punctuation + measures
    return swords

# cp dictionaries/plainwords to ~/nltk_data/corpora/stopwords/
def getPlainWords() :
    return stopwords.words("plain_words")

def getTagsWords() :
    return stopwords.words("hashtags")
