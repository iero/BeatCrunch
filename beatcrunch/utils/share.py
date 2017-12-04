import os,sys

import urllib
import urllib.request as request
from urllib.parse import urlparse

import requests

from PIL import Image # For converting image to PNG
from os.path import splitext, basename

# Twitter & Mastodon api
from TwitterAPI import TwitterAPI
from mastodon import Mastodon

# Wordpress API
from wordpress_xmlrpc import WordPressPost
from wordpress_xmlrpc import WordPressTerm
from wordpress_xmlrpc import Client
from wordpress_xmlrpc.methods import posts
from wordpress_xmlrpc.methods.posts import NewPost
from wordpress_xmlrpc.methods import taxonomies

import utils

def tweet(s,article) :
	try :
		for service in s.findall('service') :
			if service.get("name") == "twitter" :
				t = TwitterAPI(consumer_key=service.find("consumer_key").text, consumer_secret=service.find("consumer_secret").text, access_token_key=service.find("access_token_key").text, access_token_secret=service.find("access_token_secret").text)

		text = article.getTweet()
		print(u"+---[Tweet] {}".format(text.encode('utf-8')))

		if article.image :
			data = utils.services.getImageData(article.image)
			t.request('statuses/update_with_media', {'status':text}, {'media[]':data})
		else :
			t.request('statuses/update', {'status':text})

		return True
	except:
		print(u"+---[Tweet] Fail")
		# print(u"Unexpected error : {}".format( sys.exc_info()))
		return False

def toot(s,article) :
	try :
		for service in s.findall('service') :
			if service.get("name") == "mastodon" :
				m = Mastodon(client_id = service.find("client_service").text, client_secret = service.find("client_secret").text, access_token = service.find("access_token").text, api_base_url = service.find("server").text)

		text = article.getTweet()
		print(u"+---[Toot] {}".format(text.encode('utf-8')))

		if article.image :
			# print("Converting image")
			disassembled = urlparse(article.image)
			img_name, img_ext = splitext(basename(disassembled.path))
			img_local = ("/tmp/"+img_name+img_ext)

			try :
				request.urlretrieve(article.image, img_local)
				if "png" not in img_ext :
					img = Image.open(img_local)
					img_local = ("/tmp/"+img_name+".png")
					img.save("/tmp/"+img_name+".png",'png')
					os.remove("/tmp/"+img_name+img_ext)

				media_id = m.media_post(img_local)
				# print(media_id)

				m.status_post(text,in_reply_to_id=None,media_ids=[media_id])
				if os.path.exists(img_local) :
					os.remove(img_local)
				return True
			except :
				m.toot(text)
				return True
		else :
			m.toot(text)
			return True

	except:
		print(u"+---[Toot] Failed")
		return False

def publishWordPress(settings,article) :
	try:
		for s in settings.findall('service') :
			if s.get("name") == "wordpress" :
				wp = Client(s.find("server").text+'/xmlrpc.php', s.find("username").text, s.find("password").text)
				url = s.find("server").text

		# taxes = wp.call(taxonomies.GetTaxonomies())
		# print("+ Taxonomies")
		# for t in taxes :
		# 	print("+- {}".format(t))

		# Load existing tags
		aTags=[]
		availTags = wp.call(taxonomies.GetTerms('post_tag'))
		for c in availTags :
			# print("+- [{}]".format(c))
			aTags.append(str(c))

		# Add tags if new :
		addedTags = []
		for tag in article.tags :
			if tag not in aTags :
				k = tag.replace(" ", "%20")
				requests.get(url+'/add.php?tag='+k)
				addedTags.append(k)
				# print("Add tag {}".format(k))
				# print(url+'/add.php?tag='+k)
		if len(addedTags) > 0 :
			print("Added tag {}".format(','.join(addedTags)))

		# Load existing categories
		aCat=[]
		availCat = wp.call(taxonomies.GetTerms('category'))
		for c in availCat :
			# print("+- [{}]".format(c))
			aCat.append(str(c))

		# Add category if new
		#service = utils.services.getRelatedService(services,article.service)
		sName = article.service.get('name')
		if sName not in aCat :
			k = sName.replace(" ", "%20")
			requests.get(url+'/add.php?category='+k)
			print("Added category {}".format(k))

		# Length and time to read
		length = len(article.text.split())
		if length < 300 :
			tpslect = "< 1"
		else :
			t = int(length/300)
			tpslect = str(t)

		post = WordPressPost()
		post.title = article.title
		content = '<img src="'+article.image+'"/>'+article.formatedtext
		content	+= '<p><a href="'+article.url+'">Source</a></p>'
		content += '<p>'+str(length)+' words ('+ tpslect+' min)</p>'
		post.content = content
		post.post_status = 'publish'
		post.terms_names = {
	        'post_tag': article.tags,
	        'category': [sName],
		}

		wp.call(NewPost(post))

		return True
	except:
		print(u"+---[Wordpress post] Failed")
		return False
