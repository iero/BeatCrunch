import sys, os
import traceback
import gensim
import pickle

import utils
import Statistics
import Article

# Grep articles from services and extract informations
# Used to debug services

if __name__ == "__main__":

	if len(sys.argv) < 4 :
		print("Please use # python beattest.py services.xml service nb [settings]")
		sys.exit(1)
	else :
		services = utils.utils.loadxml(sys.argv[1])
		service = utils.services.getRelatedService(services,sys.argv[2])
		nb = int(sys.argv[3])


	if len(sys.argv) == 5 :
		settings = utils.utils.loadxml(sys.argv[4])

	if service is not None :
		print(u"+-[Service] [{}]".format(service.find('id').text.encode('utf-8')))
	else :
		print(u"+-[Service] [{}] not found".format(sys.argv[2]))
		sys.exit(1)

	rss_url = service.find('url').text
	url_type = service.find('url').get('type')

	# out_dir = settings.find('settings').find('output').text

	# # For debug :
	# # get last vectors
	# if os.path.exists(out_dir+'/lastvectors'):
	# 	lastvectors = pickle.load(out_dir+'/lastvectors')
	# else :
	# 	lastvectors = {}

	# Parse rss feed
	articles = []
	feedlist = []
	try :
		if url_type == "rss" :
			articles, feedlist =  utils.services.getRSSArticles(service,rss_url,[],nb)
		elif url_type == "web" :
			articles, feedlist =  utils.services.getWebArticles(service,rss_url,[],nb)
		elif url_type == "json" :
			articles, feedlist =  utils.services.getJSONArticles(service,rss_url,[],nb)
	except :
		print(u"Unexpected error")
		traceback.print_exc()

	# Load models
	dir = os.path.dirname(__file__)
	d2v_model = {}
	d2v_model['fr'] = gensim.models.doc2vec.Doc2Vec.load(os.path.join(dir, '../trained/doc2vec_fr.w2v'))
	d2v_model['en'] = gensim.models.doc2vec.Doc2Vec.load(os.path.join(dir, '../trained/doc2vec_en.w2v'))

	for a in articles :
		a.show()
		print("+---[Formated text] ")
		print(a.formatedtext.replace('</p>','</p>\n'))
		print("+---[Raw text] ")
		print(a.text)

		# utils.services.detectSimilar(d2v_model[a.lang],a,None)

		if len(sys.argv) == 5 :
			utils.share.publishWordPress(settings, a)
