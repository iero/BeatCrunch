import os, sys, time, datetime
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

def get_stopwords(lang) :

	stopset = []

	stopwords_ponctuation = [',','"',';',':','.','?','!','*','—']
	for w in stopwords_ponctuation: stopset.append(w)

	if lang == "fr" or lang == "all":
		stopwords_base = ['là','si','ça','aussi','au','aux','avec','ce','ces','dans','de','des','du','elle','en','et','eux','il','je','la','le','leur','leurs','lui','ma','mais','me','même','mes','moi','mon','ne','nos','notre','nous','on','ou','où','par','pas','pour','qu','que','qui','sa','se','ses','son','sur','ta','te','tes','toi','ton','tu','un','une','vos','votre','vous','ceci','cela','celà','cet','cette','ici','ils','les','leurs','quel','quels','quelle','quelles','sans','soi','tout','toutes','toute','tous']

		stopwords_lettres_seules = ['c','d','j','l','à','m','n','s','t','y',"c’","d’","j’","l’","m’","n’","s’","t’","qu’"]

		stopwords_verbeterne_etre = ['être','été','étée','étées','étés','étant','suis','es','est','sommes','êtes','sont','serai','seras','sera','serons','serez','seront','serais','serait','serions','seriez','seraient','étais','était','étions','étiez','étaient','fus','fut','fûmes','fûtes','furent','sois','soit','soyons','soyez','soient','fusse','fusses','fût','fussions','fussiez','fussent']
		stopwords_verbeterne_avoir = ['a','avoir','ayant','eu','eue','eues','eus','ai','as','avons','avez','ont','aurai','auras','aura','aurons','aurez','auront','aurais','aurait','aurions','auriez','auraient','avais','avait','avions','aviez','avaient','eut','eûmes','eûtes','eurent','aie','aies','ait','ayons','ayez','aient','eusse','eusses','eût','eussions','eussiez','eussent']

		for w in stopwords_base: stopset.append(w)
		for w in stopwords_lettres_seules: stopset.append(w)
		for w in stopwords_verbeterne_avoir: stopset.append(w)
		for w in stopwords_verbeterne_etre: stopset.append(w)

	if lang == "en" or lang == "all":
		stopwords_base = ['a','about','above','above','across','after','afterwards','again','against','all','almost','alone','along','already','also','although','always','among','amongst','amoungst','amount','and','another','any','anyhow','anyone','anything','anyway','anywhere','are','around','as','at','back','because','before','beforehand','behind','below','beside','besides','between','beyond','bill','both','bottom','but','by','co','con','de','describe','detail','do','done','down','due','during','each','eg','eight','either','else','elsewhere','empty','enough','etc','even','ever','every','everyone','everything','everywhere','except','few','fire','for','former','formerly','from','front','full','further','he','hence','her','here','hereafter','hereby','herein','hereupon','hers','herself','him','himself','his','how','however','hundred','i','if','in','inc','indeed','interest','into','it','its','itself','last','latter','latterly','least','less','ltd','many','me','meanwhile','mill','mine','more','moreover','most','mostly','much','must','my','myself','name','namely','neither','never','nevertheless','next','no','nobody','none','nor','not','nothing','now','nowhere','of','off','often','on','once','only','onto','or','other','others','otherwise','our','ours','ourselves','out','over','own','part','per','perhaps','please','rather','re','same','serious','several','she','side','since','sincere','so','some','somehow','someone','something','sometime','sometimes','somewhere','still','such','than','that','the','their','them','themselves','then','there','thereafter','thereby','therefore','therein','thereupon','these','they','thin','this','those','though','through','throughout','thru','thus','to','together','too','toward','towards','under','until','upon','us','very','via','we','well','were','what','whatever','when','whence','whenever','where','whereafter','whereas','whereby','wherein','whereupon','wherever','whether','which','while','whither','who','whoever','whole','whom','whose','why','with','within','without','yet','you','your','yours','yourself','yourselves','the']

		stopwords_verbs = ['am','be','became','become','becomes','becoming','been','being','call','can','cannot','cant','could','couldnt','cry','fill','find','found','get','give','go','had','has','hasnt','have','is','keep','made','may','might','move','see','seem','seemed','seeming','seems','should','show','take','put','was','will','would']

		for w in stopwords_base: stopset.append(w)
		for w in stopwords_verbs: stopset.append(w)

	return stopset

def nlp_clean(data,stopwords):
	new_str = data.lower()
	tokenizer = RegexpTokenizer(r'\w+')
	dlist = tokenizer.tokenize(new_str)
	for a in dlist :
		if len(a) < 2 :
			dlist.remove(a)
	cleanList = [word for word in dlist if word not in stopwords]
	return cleanList

def build_dataset(json_files, lang):
	docLabels = []
	data = []

	stopwords = get_stopwords(lang)

	for jfile in json_files:
		j = utils.utils.loadjson(jfile)
		for news in j :
			if news != "statistics" :
				#print(news)
				for t in j[news] :
					if t['lang'] == lang or lang == 'all':
						# Create uniq title label
						docLabels.append(news+" - "+t['title'])
						data.append(nlp_clean(t['text'],stopwords))
	return data, docLabels

def train_model(json_files,lang) :
	startime = time.time()

	data, docLabels = build_dataset(json_files,lang)
	print("{0} {1} articles loaded for model. Training..".format(len(data),lang))

	it = LabeledLineSentence(data, docLabels)

	model = gensim.models.Doc2Vec(size=300, sample=0.00001, dm=0, window=10, min_count=0, workers=8,alpha=0.024, min_alpha=0.024)
	model.build_vocab(it)
	for epoch in range(10):
		model.train(it,total_examples=model.corpus_count,epochs=model.iter)
		model.alpha -= 0.002 # decrease the learning rate
		model.min_alpha = model.alpha # fix the learning rate, no deca
		model.train(it,total_examples=model.corpus_count,epochs=model.iter)
		print(u"Epoch {0} trained - {1} min.".format(epoch, int((time.time()-startime)/60)))

	return model

def test_news(d2v_model, article, last_articles) :
	# Create vector using model
	new_vector = d2v_model.infer_vector(nlp_clean(article.text,get_stopwords(article.lang)), steps=1000, alpha=0.0025)

	# Test against model (last week)
	maxtitle = ""
	maxval = 0
	now = datetime.datetime.now()

	sims = d2v_model.docvecs.most_similar(positive=[new_vector], topn=10)
	for s in sims :
		title = s[0].split(" - ")
		title_date = datetime.datetime.fromtimestamp(int(title[0])/1000)
		oldness = now - title_date
		if 0 > oldness.days > 7 : continue
		if s[1] > maxval:
				maxval = s[1]
				maxtitle = title

	if maxval > 0 :
		td = time.strftime('%d/%m/%Y %H:%M', time.localtime(int(maxtitle[0])/1000))
		maxtitle = "{0} - {1}".format(td, maxtitle[1])
		return new_vector, maxval, maxtitle

	# Test agains last news
	# past_vectors = []
	# past_titles = []

	# if len(past_vectors) > 0 :
	# 	sim_vectors = cosine_similarity([new_vector],past_vectors)
	# 	maxidx = 0
	# 	for idx, val in enumerate(sim_vectors[0]) :
	# 		if val > 0:
	# 			maxval = max(val,maxval)
	# 			maxidx = max(idx,maxidx)

	# 	if 1 > maxval > 0.6 :
	# 		maxtitle = "{1}".format(past_titles[maxidx])
	# 		return new_vector, maxval, maxtitle

	return new_vector, 0, ""

def test_dataset(d2v_model, testList, lang):

	past_vectors = []
	past_titles = []

	nb_art=0
	found_new=0
	found_old=0

	# now = current_milli_time()

	for jfile in testList:
		print("Testing model using {0} file".format(jfile))
		d = jfile.split("/")[-1].replace('.json','')
		now = datetime.datetime(int(d[0:4]),int(d[4:6]),int(d[6:8]),00,00,00)
		outfile = open(d+'_'+lang+".csv", "w")
		outcsvtitle = d+';'+lang+';;;;\n'
		outfile.write("%s\n" % outcsvtitle)

		j = utils.utils.loadjson(jfile)
		for news in j :
			if news != "statistics" :
				for t in j[news] :
					if t['lang'] == lang or lang == 'all' :
						nb_art += 1
						found = False
						old = None
						new = None
						csv = t['title']+';'

						# Create vector using model
						new_vector = d2v_model.infer_vector(nlp_clean(t['text'],get_stopwords(lang)), steps=1000, alpha=0.0025)

						# Test against model (last week)
						maxtitle = ""
						maxval = 0
						sims = d2v_model.docvecs.most_similar(positive=[new_vector], topn=10)
						for s in sims :
							title = s[0].split(" - ")
							# oldness = now - int(title[0])
							title_date = datetime.datetime.fromtimestamp(int(title[0])/1000)
							oldness = now - title_date
							if 0 > oldness.days > 7 : continue
							if s[1] > maxval:
									maxval = s[1]
									maxtitle = title

						if 1 > maxval > 0.6 :
							found = True
						# if 1 > maxval > 0 :
							td = time.strftime('%d/%m/%Y %H:%M', time.localtime(int(maxtitle[0])/1000))
							old = "{1:.2f} ; {0} {2}".format(td, maxval, maxtitle[1])

						# Test last vectors similarity
						if len(past_vectors) > 0 :
							sim_vectors = cosine_similarity([new_vector],past_vectors)
							maxval = 0
							maxidx = 0
							for idx, val in enumerate(sim_vectors[0]) :
								if val > 0:
									maxval = max(val,maxval)
									maxidx = max(idx,maxidx)

							if 1 > maxval > 0.6 :
								found = True
								new = "{0:.2f} ; {1}".format(maxval,past_titles[maxidx])

						# Add vector to list
						past_titles.append(t['title'])
						past_vectors.append(new_vector)

						if found :
							found_new += 1
							print("+ Testing {0}".format(t['title']))
							if new is not None :
								print(new)
								csv += new + ';'
							else :
								csv += ';;'
							if old is not None :
								print(old)
								csv += old + ';'
							else :
								csv += ';;'
							if t['similarity'] >= 0.6 :
								found_old +=1
								print("+ -- Old Similarity of {0:.2f} with {1}".format(t['similarity'],t['similarity_with'].encode('utf8')))
								csv += "{0:.2f} ; {1}".format(t['similarity'],t['similarity_with'])
							else :
								csv += ';'
							print("")

						if not found :
							if t['similarity'] >= 0.6 :
								found_old +=1
								print("+ Testing {0}".format(t['title']))
								print(old)
								print("+ NOT FOUND -- Old Similarity of {0:.2f} with {1}".format(t['similarity'],t['similarity_with'].encode('utf8')))
								csv += ";;;;{0:.2f} ; {1}".format(t['similarity'],t['similarity_with'])
								print("")
							else :
								csv += ";;;;;"

						outfile.write("%s\n" % csv)

		print("{} total articles".format(nb_art))
		print("{} articles found as duplicate with old method".format(found_old))
		print("{} articles found as duplicate with new method".format(found_new))
		outfile.close()

# Load JSON raw and build corpus
def getFileLists(out_dir, testfiles) :
	json_files = sorted(glob.glob(out_dir+'/json/*.json'))

	trainList = []
	testList = []

	for f in json_files :
		cF = f.replace(out_dir+'/json/','')
		if cF in testfiles :
			testList.append(f)
		else :
			trainList.append(f)

	print("{0} files loaded for training, {1} for testing".format(len(trainList),len(testList)))
	return trainList, testList


if __name__ == "__main__":

	# Test files
	testfiles = ['20171122.json']

	if len(sys.argv) < 3 :
		print(u"Please use # python beatstats.py personal_settings.xml services.xml")
		sys.exit(1)
	else :
		settings = utils.utils.loadxml(sys.argv[1])
		services = utils.utils.loadxml(sys.argv[2])

		out_dir = settings.find('settings').find('output').text
		if not os.path.exists(out_dir+'/json'):
			print("Out dir {} not found".format(out_dir+'/json'))
			exit()

	# Load training corpus
	trainList, testList = getFileLists(out_dir,testfiles)

	# Train
	if len(sys.argv) >= 4 and sys.argv[3] == 'train' :
		if len(sys.argv) == 5 :
			lang = [sys.argv[4]]
		else :
			lang = ['fr','en']

		for l in lang :
			d2v_model = train_model(trainList,l)
			d2v_model.save(os.path.join('../trained/doc2vec_'+l+'.w2v'))
			print("{} model saved".format(l))

	# Test model
	if len(sys.argv) >= 4 and sys.argv[3] == 'test' :
		# for lang in ['fr','en'] :
		for lang in ['fr'] :
			d2v_model = gensim.models.doc2vec.Doc2Vec.load('../trained/doc2vec_'+lang+'.w2v')
			print("{} model loaded".format(lang))
			test_dataset(d2v_model, testList, lang)

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
