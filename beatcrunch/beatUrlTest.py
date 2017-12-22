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
		print("Please use # python beattest.py services.xml service url")
		sys.exit(1)
	else :
		services = utils.utils.loadxml(sys.argv[1])
		service = utils.services.getRelatedService(services,sys.argv[2])
		link = sys.argv[3]

	if service is not None :
		print(u"+-[Service] [{}]".format(service.find('id').text.encode('utf-8')))
	else :
		print(u"+-[Service] [{}] not found".format(sys.argv[2]))
		sys.exit(1)

	rss_lang = service.get('lang')
	a = Article.Article(service=service,title="test",url=link,lang=rss_lang)

	# Load models
	dir = os.path.dirname(__file__)
	d2v_model = {}
	d2v_model['fr'] = gensim.models.doc2vec.Doc2Vec.load(os.path.join(dir, '../trained/doc2vec_fr.w2v'))
	d2v_model['en'] = gensim.models.doc2vec.Doc2Vec.load(os.path.join(dir, '../trained/doc2vec_en.w2v'))

	a.show()
	print("+---[Formated text] ")
	print(a.formatedtext.replace('</p>','</p>\n'))
	print("+---[Raw text] ")
	print(a.text)

	utils.services.detectSimilar(d2v_model[a.lang],a,None)
