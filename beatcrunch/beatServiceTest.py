import sys
import traceback

import utils
import Statistics
import Article

# Grep articles from services and extract informations
# Used to debug services

if __name__ == "__main__":

	if len(sys.argv) < 3 :
		print("Please use # python beattest.py services.xml service nb")
		sys.exit(1)
	else :
		services = utils.utils.loadxml(sys.argv[1])
		service = utils.services.getRelatedService(services,sys.argv[2])

	if len(sys.argv) == 4 :
		nb = int(sys.argv[3])
	else :
		nb = 5

	if service is not None :
		print(u"+-[Service] [{}]".format(service.find('id').text.encode('utf-8')))
	else :
		print(u"+-[Service] [{}] not found".format(sys.argv[2]))
		sys.exit(1)

	rss_url = service.find('url').text
	url_type = service.find('url').get('type')

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

	for a in articles :
		a.show()
		utils.services.detectAdArticle(service,a)
		utils.services.rateArticle(service,a)
