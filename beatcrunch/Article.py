import time
import re
import pytz

from urllib.parse import urlparse # parse url
from datetime import datetime
from bs4 import NavigableString, Comment

import utils

current_milli_time = lambda: int(round(time.time() * 1000))

#Todo :
# Compter nombre de liens vers l'externe dans le texte

# Stocker vecteur fait depuis le dernier modèle

class Article:
	nbarticles = 0

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

		# Get domain
		entry_parsed = urlparse(self.url)
		self.domain = '{uri.netloc}'.format(uri=entry_parsed)

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
		self.raw=""

		# Look for 10 most common tags in title+text
		self.tags = utils.similarity.findTags(self.title+". "+self.text,self.lang,10)
		# print(uself.tags)

		self.formatedtext=self.getFormatedText()

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
			# Filter ads
			if self.service.find('sanitize') is not None :
				for san in self.service.find('sanitize').findall("remove") :
					for div in text_sec.find_all(san.get('section'), {san.get('type'):san.text}):
						div.decompose()

			for s in text_sec.find_all('script') :
				s.extract()

			if ',' in section :
				section = section.split(',')[0]

			for t in text_sec.find_all(section):
				if len(out_text)>1 and out_text.strip()[-1] == '.' :
					out_text = out_text + " "
				out_text=out_text+utils.textutils.sanitizeText(self.service, t.get_text())

		return out_text

	# Get images, lists, italics.. and not only text.
	def getFormatedText(self) :
		# nb characters before <!-- more -->
		max_preview_size : 100

		img_list=[]
		link_list=[]

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

			# Remove ads defined in services file (<sanitize><remove/></sanitize>)
			if self.service.find('sanitize') is not None :
				for san in self.service.find('sanitize').findall("remove") :
					for div in text_sec.find_all(san.get('section'), {san.get('type'):san.text}):
						div.decompose()

			# Remove scripts
			for s in self.soup('script') :
				s.extract()

			# Detect unnecessary tags and crappy attributes in original soup
			tags_to_keep = ['div','a','p','img','ul','li','i']
			tags_to_remove = []

			attributes_to_keep = ['src','href']
			attributes_to_remove = []

			for tag in self.soup.find_all(True):
				# Tag
				if tag.name not in tags_to_keep and tag.name not in tags_to_remove :
					tags_to_remove.append(tag.name)

				# Attribute
				for attr in tag.attrs :
					if attr not in attributes_to_keep and attr not in attributes_to_remove :
						attributes_to_remove.append(attr)

			# Remove unnecessary tags but keep content
			# print("+---[Remove tags] {}".format(','.join(tags_to_remove)))
			for tag in tags_to_remove :
				for t in text_sec.find_all(tag) :
					t.replaceWithChildren()

			# Remove attributes
			# print("+---[Remove attributes] {}".format(','.join(attributes_to_remove)))
			for attribute in attributes_to_remove :
				for tag in text_sec.findAll():
					del(tag[attribute])

			# Remove empty tags (TO TEST)
			for tag in tags_to_keep :
				for t in text_sec.find_all(tag) :
					# Test if no children or no content
					if len(t.contents) == 0 and len(t.attrs) == 0 :
						t.decompose()

			# Debug
			# print(text_sec)

			# Keep usefull stuff (text, images, links..)
			for s in text_sec.descendants :
				# Contains text (not comment) and parent is not a link
				# Normaly get <p>text</p> and text<br/> stuff
				if s.name == None and s.parent.name != 'a' and not isinstance(s, Comment):
					s_content = str(s).strip()
					if len(s_content) > 0 :
						s_text = self.internal_addText(s_content)
						# if starts with letter, add space before.
						if len(s_text) > 0 and s_text[0].islower() :
							s_text = ' '+s_text
						out_text += s_text

				# link with content (image or text)
				elif s.name == 'a' and s.content != None :
					s_content = str(s.contents[0])
					# get urls
					if self.domain not in s['href'] and s['href'] not in link_list :
						link_list.append(s['href'])

					# image in link
					if s.contents[0].name != None and 'img' in s.contents[0].name :
						s_image = s.contents[0]['src']
						if s_image not in img_list and not s_image in self.image :
							img_list.append(s_image)
							# print("[a {0}]\n {1}\n[/a] ".format(s['href'],s_image))
							out_text += '<a href="'+s['href']+'">'+s_content+'</a>'

					# text in link
					else :
						# print("[a {0}] {1} [/a] ".format(s['href'],s_content))
						out_text += '<a href="'+s['href']+'">'+s_content+'</a>'

				# don't understand why
				elif s.name == 'a' :
					# get urls
					if self.domain not in s['href'] and s['href'] not in link_list :
						link_list.append(s['href'])
					out_text += str(s)

				# img without associated link
				elif s.name == 'img' and s.parent.name != 'a' :
					# print("[img] {0} [/img] ".format(s['src']))
					s_image = s['src']
					if s_image not in img_list and not s_image in self.image :
						img_list.append(s_image)
						out_text += '<img src="'+s['src']+'"/>'
				elif s.name == 'p' :
					out_text += '<br/>'
				# elif s.name == 'ul' :
				#   print("[{}]".format(s.name))
				#   out_text += str(s)
				# elif s.name == 'i' :
				#   print("[{}]".format(s.name))
				#   out_text += str(s)
				# debug
				# elif s.name != None :
				#   print("[others] {}".format(s.name))
				#   print(s)

		self.nb_images = len(img_list)
		self.nb_links = len(link_list)

		#Remove first <br/>
		if out_text.startswith('<br/>') :
			out_text = out_text.replace('<br/>','',1)

		# Add more for preview
		end_sentences = [m.start() for m in re.finditer('[.!?;] ', out_text)]
		occ_to_replace = 0
		for end in end_sentences :
			if end <= 200 :
				occ_to_replace = end+1

		if occ_to_replace > 0 :
			out_text = out_text[:occ_to_replace] + '<!--more-->' + out_text[occ_to_replace:]
		else :
			out_text = out_text[:200] + '<!--more-->' + out_text[200:]

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

		if self.nb_images > 0 :
			print(u'+---[{} images]'.format(self.nb_images))

		if self.nb_links > 0 :
			print(u'+---[{} links]'.format(self.nb_links))

	def internal_addText(self,text) :
		if text[-1:] != ' ' :
			text += ' '
		# if not text.startswith('<p>') and not text.endswith('</p>') :
		#   text = '<p>'+text+'</p>'

		# Add spaces near ponctuation and remove extra spaces :
		text = re.sub('([!?(])', r' \1', text)
		text = re.sub('([.,!?)])', r'\1 ', text)
		text = re.sub('\s{2,}', ' ', text)

		return text
