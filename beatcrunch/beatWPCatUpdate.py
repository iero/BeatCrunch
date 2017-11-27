import sys
import utils

import requests

from wordpress_xmlrpc import Client
from wordpress_xmlrpc.methods import taxonomies
from wordpress_xmlrpc import WordPressTerm

if __name__ == "__main__":

	if len(sys.argv) < 3 :
		print(u"Please use # python file.py settings.xml services.xml")
		sys.exit(1)
	else :
		settings = utils.utils.loadxml(sys.argv[1])
		services = utils.utils.loadxml(sys.argv[2])

	print("update categories in {}".format(sys.argv[1]))

	# Get whole service list
	sList = []
	for s in services.findall('service'):
		sList.append(s.get('name'))
		#print(s.get('name'))

	# Get available categories
	for s in settings.findall('service') :
		if s.get("name") == "wordpress" :
			wp = Client(s.find("server").text+'/xmlrpc.php', s.find("username").text, s.find("password").text)
			url = s.find("server").text

	taxes = wp.call(taxonomies.GetTaxonomies())
	print("+ Taxonomies")
	for t in taxes :
		print("+- {}".format(t))

	sCat=[]
	print("+ Categories")
	categories = wp.call(taxonomies.GetTerms('category'))
	for c in categories :
		print("+- [{}]".format(c))
		sCat.append(str(c))

	for c in sList :
		k = c.replace(" ", "%20")
		if c not in sCat :
			r = requests.get(url+'/add.php?category='+k)
			print("+ Add {}".format(k))



	# Add category
	# print("test")
	# parent_cat = wp.call(taxonomies.GetTerm('category', 3))
	# for c in parent_cat :
	# 	print("+ {}".format(c))

	# Create child category
	# parent_cat = wp.call(taxonomies.GetTerm('category', 3))
	# child_cat = WordPressTerm()
	# child_cat.taxonomy = 'category'
	# child_cat.parent = parent_cat.id
	# child_cat.name = 'My Child Category'
	# child_cat.id = client.call(taxonomies.NewTerm(child_cat)

	#Create tag
	# tag = WordPressTerm()
	# tag.taxonomy = 'my-category'
	# tag.name = 'apple'
	# tag.id = wp.call(taxonomies.NewTerm(tag))

	# for s in settings.find('settings').find("services").findall('service'):
	# 	print(s.text)


