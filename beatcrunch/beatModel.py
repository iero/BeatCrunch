import os, sys, time
import re
import json
import glob

from nltk import RegexpTokenizer
from nltk.corpus import stopwords

import gensim
from gensim.models.doc2vec import LabeledSentence
from sklearn.metrics.pairwise import cosine_similarity

import utils

current_milli_time = lambda: int(round(time.time() * 1000))

class LabeledLineSentence(object):
	def __init__(self, doc_list, labels_list):
		self.labels_list = labels_list
		self.doc_list = doc_list
	def __iter__(self):
		for idx, doc in enumerate(self.doc_list):
			yield gensim.models.doc2vec.LabeledSentence(doc,[self.labels_list[idx]])

def build_dataset(json_files, stopwords):
	docLabels = []
	data = []

	for jfile in json_files:
		j = utils.utils.loadjson(jfile)
		for news in j :
			if news != "statistics" :
				#print(news)
				for t in j[news] :
					if t['lang'] == 'fr' :
						# Create uniq title label
						docLabels.append(news+" - "+t['title'])
						data.append(nlp_clean(t['text'],stopwords))
	return data, docLabels

def train_model(json_files,stopwords) :
	startime = time.time()

	data, docLabels = build_dataset(json_files,stopwords)
	print("{0} articles loaded for model".format(len(data)))

	it = LabeledLineSentence(data, docLabels)

	model = gensim.models.Doc2Vec(size=300, sample=0.00001, dm=0, window=10, min_count=0, workers=8,alpha=0.024, min_alpha=0.024)
	model.build_vocab(it)
	for epoch in range(10):
		print("Training epoch {}".format(epoch))
		model.train(it,total_examples=model.corpus_count,epochs=model.iter)
		model.alpha -= 0.002 # decrease the learning rate
		model.min_alpha = model.alpha # fix the learning rate, no deca
		model.train(it,total_examples=model.corpus_count,epochs=model.iter)
		print(u" {} min - Epoch trained.".format(int((time.time()-startime)/60)))


	#saving the created model
	model.save(os.path.join('../trained/doc2vec.w2v'))
	print('model saved')

def test_dataset(d2v_model, json_files, stopwords):

	past_vectors = []
	past_titles = []

	now = current_milli_time()

	for jfile in json_files:
		print("Testing model using {0} file".format(jfile))
		j = utils.utils.loadjson(jfile)
		for news in j :
			if news != "statistics" :
				#print(news)
				for t in j[news] :
					if t['lang'] == 'fr' :
						# Create uniq title label
						# print("Test with {0} {1}".format(news,t['title']))
						new_vector = d2v_model.infer_vector(nlp_clean(t['text'],get_stopwords()), steps=1000, alpha=0.0025)
						sims = d2v_model.docvecs.most_similar(positive=[new_vector], topn=10)

						# Test last vectors similarity
						if len(past_vectors) > 0 :
							sim_vectors = cosine_similarity([new_vector],past_vectors)
							for idx, val in enumerate(sim_vectors[0]) :
								if val > 0.6:
									print("Found something as {0}".format(t['title']))
									print("{0} {1:.2f} {2}".format(idx,val,past_titles[idx]))
									print(" ")

						past_titles.append(t['title'])
						past_vectors.append(new_vector)

						# for s in sims :
						# 	title = s[0].split(" - ")
						# 	oldness = now - int(title[0])

						# 	# if oldness > 2629800000 : continue # un mois
						# 	if oldness > 604800000 : continue # une semaine
						# 	# For output
						# 	if s[1] >= 0.55 :
						# 		print("Test with {0} {1}".format(news,t['title']))
						# 		td = time.strftime('%d/%m/%Y %H:%M', time.localtime(int(title[0])/1000))
						# 		print("{0} [{1:.2f}] {2}".format(td, s[1], title[1]))
						# 		break


						# print(' ')
							# For excel
							# td = time.strftime('%d/%m/%Y', time.localtime(int(title[0])/1000))
							# print("{0};{1:.2f}".format(td, s[1]))


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
	# json_files = sorted(glob.glob(out_dir+'/json/*.json'))
	# train_model(json_files,get_stopwords())

	#load the model
	d2v_model = gensim.models.doc2vec.Doc2Vec.load('../trained/doc2vec.w2v')

	json_file = sorted(glob.glob(out_dir+'/test.json'))
	test_dataset(d2v_model, json_file, get_stopwords())

	# Test with text existing in training set
	# print("Test with kwown text")
	# print('Results : ')
	# sims = d2v_model.docvecs.most_similar(positive=['1500584801776 - Sega débarque du passé sur les mobiles'])
	# for s in sims :
	# 	print(s)

	# Test with text outside training text
	# print("Test with unkwown text")
	# newdoc="Dévoilée pendant le dernier CES, la nouvelle smartwatch de Misfit embarque un écran AMOLED rond de 1,39 pouces et d'une résolution de 326ppp, ainsi qu'un processeur Snapdragon Wear 2100, un accéléromètre, un altimètre, un gyroscope, un cardiofréquencemètre, un GPS et un micro. Tous ces capteurs permettront à la Vapor de surveiller la plupart des activités sportives sans dépendre d'un smartphone, et même de diffuser dans un casque bluetooth la musique stockée dans sa mémoire de 4Go. La smartwatch se démarquera par ailleurs par sa lunette tactile, laquelle pourra par exemple être utilisée pour naviguer dans les applications en faisant glisser son doigt autour de l'écran et en cliquant sur le bouton latéral. Misfit promet enfin une autonomie d'environ deux jours entre deux charges. La Vapor sera en vente le 31 octobre au prix de 199$ sur le site du constructeur."

	# print('Devrait trouver 1508966362314 - Misfit lancera finalement sa Vapor le 31 octobre')
	# print('Results : ')
	# new_vector = d2v_model.infer_vector(nlp_clean(newdoc,get_stopwords()), steps=1000, alpha=0.0025)
	# sims = d2v_model.docvecs.most_similar(positive=[new_vector])
	# for s in sims :
	# 	print(s)
