# -*-coding:utf-8 -*
import sys

import utils

if __name__ == "__main__":

	if len(sys.argv) < 3 :
		print(u"Please use # python file.py settings.xml services.xml")
		sys.exit(1)
	else :
		settings = utils.utils.loadxml(sys.argv[1])
		services = utils.utils.loadxml(sys.argv[2])


	print("Test settings in {}".format(sys.argv[1]))
	# Get Services list
	sList_global = {}

	sList_selected = []
	sList_ok = []
	sList_missing = []
	sList_notavailable = []

	# Get whole list
	for s in services.findall('service'):
		sList_global[s.find('id').text] = s.get('name')

	# Get new articles for each selected service
	for s in settings.find('settings').find("services").findall('service'):
		sList_selected.append(s.text)

		if s.text in sList_global :
			sList_ok.append(s.text)
		else :
			sList_notavailable.append(s.text)

	# Check if all services are selected
	for s in sList_global :
		if s not in sList_selected :
			sList_missing.append(sList_global[s])

	print("[{}] services available".format(len(sList_global)))
	print("[{}] in use".format(len(sList_ok)))

	print("[{}] not in use : ".format(len(sList_missing)))
	for s in sList_missing :
		print(" - {}".format(s))

	print("[{}] not available anymore : ".format(len(sList_notavailable)))
	for s in sList_notavailable :
		print(" - {}".format(s))

	nb=3
	print("\n\nCheck if services works with {} articles checks : ".format(nb))
	for s in sList_global :
		service = utils.services.getRelatedService(services,s)
		print(u"+-[Service] [{}]".format(service.find('id').text.encode('utf-8')))

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

		nb_images = 0
		nb_words = 0
		nb_tags = 0
		for a in articles :
			# a.show()
			if a.image :
				nb_images += 1
			nb_words += len(a.text.split())
			nb_tags += len(a.tags)
			# utils.services.detectAdArticle(service,a)
			# utils.services.rateArticle(service,a)

		warning=False
		if nb_words < nb*100 :
			print("WARNING  : Only {} words found".format(nb_words))
			warning=True
		if nb_images < nb/2 :
			print("WARNING  : Only {} images found".format(nb_images))
			warning=True
		if nb_words < nb*10/2 :
			print("WARNING  : Only {} tags found".format(nb_tags))
			warning=True

		if not warning :
			print("+--[OK] All good with {0} words, {1} images, and {2} tags".format(nb_words,nb_images,nb_tags))
		else :
			print("+--[WARNING] Found {0} words, {1} images, and {2} tags".format(nb_words,nb_images,nb_tags))
