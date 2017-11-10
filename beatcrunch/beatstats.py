import os, sys, time
import re
import json
import glob
import multiprocessing #concurrency
import operator
import string

from random import randint

import nltk
from nltk import ngrams
from nltk.corpus import stopwords

import gensim.models.word2vec as w2v

import sklearn.manifold #dimensionality reduction
import pandas as pd #parse dataset
# import numpy as np #math
# import matplotlib #plotting
# import matplotlib.pyplot as plt
# import seaborn as sns #visualization

import utils

# problem : need to break sentences in words

def clean_stopwords(sentence) :
	stopwords_french_3 = set(line.strip() for line in open('../dictionaries/stopwords_fr3'))
	for w in stopwords_french_3 :
		sentence = sentence.replace(w,"")

	stopwords_french_2 = set(line.strip() for line in open('../dictionaries/stopwords_fr2'))
	for w in stopwords_french_2 :
		sentence = sentence.replace(w,"")

	stopwords_french_1 = set(line.strip() for line in open('../dictionaries/stopwords_fr1'))
	for w in stopwords_french_1 :
		sentence = sentence.replace(w,"")

	return sentence

def sentence_to_wordlist(sentence):
	clean = re.sub(r'\W+', ' ', sentence)
	words = clean.split()
	return words

def sentence_to_ngrams(sentence,n):
	n_grams=[]
	xgrams = ngrams(sentence.split(), n)
	for grams in xgrams :
		n_grams.append(' '.join(grams))

	return n_grams

def freqDist(tokens):
	dist={}
	for t in tokens :
		#if len(t) == 1 : continue

		if t in dist :
			dist[t] += 1
		else :
			dist[t] = 1

	out=[]
	# a=0
	for (k,v) in sorted(dist.items(), key=operator.itemgetter(1), reverse=True) :
		if v>1 :
			out.append(k)
			# if a<200 : print("{0} {1}".format(v,k))
			# a += 1
		# if v==1 : dist.pop(k)

	return out

def load_json_files(json_files) :
	startime = time.time()

	corpus_raw_french = u""
	# corpus_raw_english = u""

	words=[]
	bigrams=[]
	trigrams=[]

	for jfile in json_files:
		j = utils.utils.loadjson(jfile)
		for news in j :
			if news != "statistics" :
				for t in j[news] :
					if t['lang'] == 'fr' :
						raw_text = t['title']+". "+t['text']

						# Add space after end of sentence, followed by Capital letter.
						raw_text= re.sub(r'\.([a-zA-Z])', r'. \1', raw_text)
						raw_text= re.sub(r'\!([a-zA-Z])', r'. \1', raw_text)
						raw_text= re.sub(r'\?([a-zA-Z])', r'. \1', raw_text)

						raw_sentences=raw_text.split('. ')

						for sentence in raw_sentences :
							# Remove ponctiation
							# translator = str.maketrans('', '', string.punctuation)
							# sentence = sentence.translate(translator)
							sentence = clean_stopwords(sentence)

							# for w in sentence_to_ngrams(sentence,1) :
							# 	words.append(w)
							for w in sentence_to_ngrams(sentence.lower(),1) :
								words.append(w)
							# for w in sentence_to_ngrams(sentence,2) :
							# 	bigrams.append(w)
							for w in sentence_to_ngrams(sentence.lower(),2) :
								bigrams.append(w)
							# for w in sentence_to_ngrams(sentence,3) :
							# 	trigrams.append(w)
							for w in sentence_to_ngrams(sentence.lower(),3) :
								trigrams.append(w)

	print("{0:,} words detected, with most frequents :".format(len(words)))
	dist = freqDist(words)
	print(dist[1:100])
	# with open("../dictionaries/stopwords_fr1", "a") as myfile:
	# 	for i in range(0, 200) :
	# 	    myfile.write(dist[i]+'\n')

	print("{0:,} bigrams detected, with most frequents :".format(len(bigrams)))
	dist = freqDist(bigrams)
	print(dist[1:100])
	# with open("../dictionaries/stopwords_fr2", "a") as myfile:
	# 	for i in range(0, 200) :
	# 	    myfile.write(dist[i]+'\n')

	print("{0:,} trigrams detected, with most frequents :".format(len(bigrams)))
	dist = freqDist(trigrams)
	print(dist[1:100])
	# with open("../dictionaries/stopwords_fr3", "a") as myfile:
	# 	for i in range(0, 200) :
	# 	    myfile.write(dist[i]+'\n')

					# else :
						# corpus_raw_english += t['text']
		# print("Adding '{0}' : English corpus is now {1:,} characters long".format(jfile,len(corpus_raw_english)))
		# print("Adding '{0}' : French corpus is now {1:,} characters long".format(jfile,len(corpus_raw_french)))

	# print("English corpus is {0:,} characters long".format(len(corpus_raw_english)))
	# print("French corpus is {0:,} characters long".format(len(corpus_raw_french)))

	# #tokenize corpus into sentences
	# tokenizer_english = nltk.data.load('tokenizers/punkt/english.pickle')
	# tokenizer_french = nltk.data.load('tokenizers/punkt/french.pickle')
	# raw_sentences_english = tokenizer_english.tokenize(corpus_raw_english)
	# raw_sentences_french = tokenizer_french.tokenize(corpus_raw_french)

	# print ("{0:,} raw english sentences".format(len(raw_sentences_english)))
	# print ("{0:,} raw french sentences".format(len(raw_sentences_french)))

	# # add each sentence in list, removing stopwords
	# sentences_english = []
	# sentences_french = []

	# stops_english = set(stopwords.words("english"))
	# stops_french = set(stopwords.words("french"))

	# for raw_sentence in raw_sentences_english:
	# 	raw_words = sentence_to_wordlist(raw_sentence)
	# 	filtered_sentence = [word for word in raw_words if word.lower() not in stops_english]
	# 	if len(filtered_sentence) > 0:
	# 		sentences_english.append(filtered_sentence)

	# for raw_sentence in raw_sentences_french:
	# 	raw_words = sentence_to_wordlist(raw_sentence)
	# 	filtered_sentence = [word for word in raw_words if word.lower() not in stops_french]
	# 	if len(filtered_sentence) > 0:
	# 		sentences_french.append(filtered_sentence)


	# #print an example
	# print("Example in english")
	# print(sentences_english[randint(0, 1000)])
	# print("Example in french")
	# print(sentences_french[randint(0, 1000)])

	# #count tokens, each one being a sentence
	# token_count_english = sum([len(sentence) for sentence in sentences_english])
	# token_count_french = sum([len(sentence) for sentence in sentences_french])
	# print("The raw english book corpus contains {0:,} tokens".format(token_count_english))
	# print("The raw french book corpus contains {0:,} tokens".format(token_count_french))

	# print(u"Corpus built in {} s".format(int(time.time()-startime)))

	# return sentences_english, sentences_french

def build_model(sentences):
	startime = time.time()

	#define hyperparameters

	# Dimensionality of the resulting word vectors.
	# more dimensions mean more training , but more generalized
	num_features = 300

	# Minimum word count threshold. Smallest set of word we want to recognize
	min_word_count = 3

	# Number of threads to run in parallel.
	num_workers = multiprocessing.cpu_count()

	# Context window length. Looking at blocks that contains X words at a time
	context_size = 7

	# Downsample setting for frequent words (good between 0 and 1e-5)
	# The more frequent a word is, the less often we want tu use it
	downsampling = 1e-3

	# Seed for the Random Number Generator, to make the results reproducible.
	# Make the seed deterministic
	seed = 1

	vec = w2v.Word2Vec(
		sg=1,
		seed=seed,
		workers=num_workers,
		size=num_features,
		min_count=min_word_count,
		window=context_size,
		sample=downsampling
	)

	vec.build_vocab(sentences)
	print("Word2Vec vocabulary length:", len(vec.wv.vocab))

	# Train model on sentences

	token_count = sum([len(sentence) for sentence in sentences])
	vec.train(sentences,total_examples=token_count, epochs=vec.iter)

	print(u"Trained model in {} s".format(int(time.time()-startime)))

	return vec

def save_model(vec,name):
	if not os.path.exists("../trained"):
		os.makedirs("../trained")
	vec.save(os.path.join("../trained", name+".w2v"))

def create_2d_matrix(vec,name):
	startime = time.time()
	#squash 300 dimensions to 2
	tsne = sklearn.manifold.TSNE(n_components=2, random_state=0)

	#put it all into a giant matrix
	all_word_vectors_matrix = vec.wv.syn0
	#train tsne
	all_word_vectors_matrix_2d = tsne.fit_transform(all_word_vectors_matrix)

	print(u"Matrix created in {} min".format(int((time.time()-startime)/60)))

	points = pd.DataFrame(
		[
			(word, coords[0], coords[1])
			for word, coords in [
				(word, all_word_vectors_matrix_2d[vec.wv.vocab[word].index])
				for word in vec.wv.vocab
			]
		],
		columns=["word", "x", "y"]
	)

	# Save 2D rep
	df.to_pickle("trained/"+mane+".pkl")

if __name__ == "__main__":

	if len(sys.argv) < 3 :
		print(u"Please use # python beatstats.py settings.xml services.xml")
		sys.exit(1)
	else :
		settings = utils.utils.loadxml(sys.argv[1])
		services = utils.utils.loadxml(sys.argv[2])

		out_dir = settings.find('settings').find('output').text
		if not os.path.exists(out_dir+'/json'):
			print("Out dir {} not found".format(out_dir+'/json'))
			exit()

	# # Load JSON raw and build corpus
	json_files = sorted(glob.glob(out_dir+'/json/*.json'))
	load_json_files(json_files)
	# sentences_english, sentences_french = load_json_files(json_files)

	# # train and save modens
	# vec_eng = build_model(sentences_english)
	# vec_fr = build_model(sentences_french)

	# save_model(vec_eng,"vec_english")
	# save_model(vec_fr,"vec_french")

	# Load models
	# vec_eng = w2v.Word2Vec.load(os.path.join("../trained", "vec_english.w2v"))
	# vec_fr = w2v.Word2Vec.load(os.path.join("../trained", "vec_french.w2v"))

	# Save 2D rep
	# create_2d_matrix(vec_eng,"vec_english")
	# create_2d_matrix(vec_fr,"vec_french")

	# print(vec_eng.wv.most_similar(positive="Apple"))
	# print(vec_eng.wv.most_similar(positive="apple"))
	# print(vec_fr.wv.most_similar(positive="Apple"))
	# print(vec_fr.wv.most_similar(positive="apple"))
