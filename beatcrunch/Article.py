import time
import re
import pytz

from datetime import datetime
from urllib.parse import urlparse

import utils

current_milli_time = lambda: int(round(time.time() * 1000))

class Article:
	nbarticles = 0

	# def __init__(self, service, title, url, lang):
		# startime = time.time()
	def __init__(self, *args, **kwargs):
		# Object Creation
		self.id = str(current_milli_time())
		self.date = datetime.now(pytz.timezone('Europe/Paris')).isoformat(),

		# Mandatory
		if kwargs.get('service') :
			self.service = kwargs.get('service')
		if kwargs.get('title') :
			self.title = kwargs.get('title')
		if kwargs.get('url') :
			self.url = kwargs.get('url')
		if kwargs.get('lang') :
			self.lang = kwargs.get('lang')

		print(u"+--[Parsing] {}".format(self.title))

		# From service
		self.service_name = self.service.find('id').text
		self.service_mention = self.service.find('mention').text

		# print(u"+--[{}] {} {} {}".format(self.service_name, self.lang,self.title,self.url))

		if kwargs.get('content') :
			self.soup = utils.services.getArticleContentFromText(kwargs.get('content'))
		else :
			self.soup = utils.services.getArticleContentFromUrl(self.url)
			# print(uself.soup)

		if kwargs.get('image') :
			self.image = kwargs.get('image')
		else :
			self.image = self.getMainImage()

		self.shorturl = self.url
		self.text=self.getText()
		self.formatedtext=self.getFormatedText()
		self.raw=""

		# Look for 10 most common tags in title+text
		self.tags = utils.similarity.findTags(self.title+". "+self.text,self.lang,10)
		# print(uself.tags)

		self.rate=0
		self.similarity=0
		self.similarity_with=""

		self.liked=0

		#print(u"+-[Article] {} ".format(self.lang))
		# self.show()
		Article.nbarticles += 1
		# print(u"+---[Proceed] in {} s".format(int(time.time()-startime)))

	def getMainImage(self) :
		out_img=""
		if self.service.find('image') is not None :
			type = self.service.find('image').get('type')
			value = self.service.find('image').text
			name = self.service.find('image').get('name')

			if type == "meta" :
				if name == "property" :
					url = self.soup.find(type, property=value)
				elif name == "name" :
					url = self.soup.find(type, {"name":value})

				if url is not None :
					out_img = url["content"]

			elif type == "div" :
				section = self.service.find('image').get('section')
				attribute = self.service.find('image').get('attribute')

				if name == "class" :
					img_sec=self.soup.find(type, class_=value)
				else :
					img_sec=self.soup.find(type, {name: value})

				if img_sec is not None and self.service.find('image').get('subtype') is not None :
					subtype = self.service.find('image').get('subtype')
					img_sec = img_sec.find(subtype)
					# print(img_sec)

				if img_sec is not None and img_sec.find(section) is not None :
					out_img=img_sec.find(section).get(attribute)

		else :
			return ""

		out_img = utils.services.sanitizeImage(self.service,out_img)
		return utils.services.sanitizeUrl(self.url,out_img)

	def getText(self) :
		out_text=""
		if self.service.find('text') is not None :
			type = self.service.find('text').get('type')
			name = self.service.find('text').get('name')
			value = self.service.find('text').text
			section = self.service.find('text').get('section')
		else :
			return out_text

		if (name == "class") :
			text_sec=self.soup.find(type, class_=value)
			# print(text_sec)
		elif name == "None" :
			text_sec=self.soup
		else :
			text_sec=self.soup.find(type, {name: value})

		if text_sec is not None :
			for t in text_sec.find_all(section):
				if len(out_text)>1 and out_text.strip()[-1] == '.' :
					out_text = out_text + " "
				out_text=out_text+utils.utils.sanitizeText(t.get_text())

		return out_text

	# TODO: Get images and not only text.

	def getFormatedText(self) :
		out_text=""
		if self.service.find('text') is not None :
			type = self.service.find('text').get('type')
			name = self.service.find('text').get('name')
			value = self.service.find('text').text
			section = self.service.find('text').get('section')
		else :
			return out_text

		if name == "class" :
			text_sec=self.soup.find(type, class_=value)
		elif name == "None" :
			text_sec=self.soup
		else :
			text_sec=self.soup.find(type, {name: value})

		if text_sec is not None :
			for t in text_sec.find_all(section):
				sText=utils.utils.sanitizeText(t.get_text())
				if sText :
					if len(out_text)>1 and out_text.strip()[-1] == '.' :
						out_text = out_text + " "
					out_text=out_text+"<p>"+sText+"</p>"
		return out_text

	def printJson(self) :
		return {
			'title': self.title,
			'service': self.service_name,
			'source': self.url,
			'shorturl': self.shorturl,
			'date' : self.date,
			'lang' : self.lang,
			'image': self.image,
			'tags' : self.tags,
			'rate' : self.rate,
			'similarity' : self.similarity,
			'similarity_with' : self.similarity_with,
			'text' : self.text,
			'text_size' : str(len(self.text.split())),
			'text_formated' : self.formatedtext,
			'liked' : self.liked
		}

	def getTweet(self) :
		#TODO : pass tweet size in arg
		tweet_size = 280
		tweet_link_size = 24

		text=self.title
		# print(u"[Tweet] Text : [{}]".format(text))
		# Add '#' in front of the 3 main tags if in title
		max=3
		nb=0
		if self.tags :
			for w in self.tags :
				if nb >= max : break
				# print(u"[Tweet] Look for {} in [{}]".format(w,text))
				# Verify if we can add a #
				if w in text.lower() :
					# print(u"[Tweet] Found {}".format(w))

					for v in re.split(' |; |, |\'',text) :
						# print(u"[Tweet] Try to Replace {} using {}".format(v,v.lower()))
						if w == v.lower() and len(text)+tweet_link_size+1 <= tweet_size :
							text = re.sub(v,'#'+w,text)
							# First matched tag is enough
							nb=max
							# Just replace first occurence
							break
				nb += 1
		# print(u"[Tweet] Add Tags : [{}]".format(text))

		# Add source if possible
		if len(text)+len(self.service_mention)+2+tweet_link_size <= tweet_size and self.service_mention not in text :
			text += " "+self.service_mention
		# print(u"[Tweet] Add source : [{}]".format(text))

		# Add url
		# Add main tag after url if not in title
		if len(self.tags) >= 1 :
			maintag = self.tags[0]
			if " " not in maintag and maintag not in text and len(text)+len(maintag)+2+tweet_link_size <= tweet_size :
				text += " "+self.shorturl+" #"+maintag
			else :
				text += " "+self.shorturl
		else :
			text += " "+self.shorturl

		return text

	def show(self) :
		print(u"+--[Article] {} ".format(self.title.encode('utf8')))

		# Length and time to read
		length = len(self.text.split())
		if length < 300 :
			tpslect = "< 1"
		else :
			t = int(length/300)
			tpslect = str(t)
		print(u"+---[content] {} words ({} min)".format(str(length),tpslect))

		# URL
		print(u"+---[url] {} ".format(self.url.encode('utf8')))
		if self.image : print(u"+---[img] {} ".format(self.image.encode('utf8')))

		# Tags
		if (len(self.tags) > 0 ) :
			tags = ','.join(self.tags)
			print(u"+---[tags] [{}]".format(tags.encode('utf8')))
