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

		# Sources
		self.img_list=[]
		self.link_list=[]

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

		# Main image found : add to image list
		if self.image :
			self.img_list.append(self.image)

		self.shorturl = self.url
		self.text=self.getText()
		self.raw=""

		# Look for 10 most common tags in title+text
		self.tags = utils.similarity.findTags(self.title+". "+self.text,self.lang,10)
		# print(uself.tags)

		self.formatedtext=self.getFormatedText()

		# No main image : try to add the first from the article
		if not self.image and len(self.img_list) > 0 :
			self.image = self.img_list[0]

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
		elif name== "rss" or name == "None" :
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
		# nb of characters before <!-- more -->
		more_size = 200
		added_more = False

		# Debug
		# print(self.soup.prettify())

		out_text=""
		if self.service.find('text') is not None :
			type = self.service.find('text').get('type')
			name = self.service.find('text').get('name')
			value = self.service.find('text').text
			section = self.service.find('text').get('section')
		else :
			return ""

		if name == "class" :
			text_sec=self.soup.find(type, class_=value)
		elif name== "rss" or name == "None" :
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

			# Clean input
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

			# Remove empty tags
			for tag in tags_to_keep :
				for t in text_sec.find_all(tag) :
					# Test if no children or no content
					if len(t.contents) == 0 and len(t.attrs) == 0 :
						t.decompose()

			# Debug
			# print(text_sec.prettify())

			# Keep usefull stuff (text, images, links..)
			in_p = False
			for s in text_sec.descendants :
				# Doctype
				if str(s).startswith('html PUBLIC') : continue

				# debug
				# print("[{0}] {1}".format(s.name,str(s)))

				# Find if still in <p/>
				found_p = False
				for parent in s.parents :
					if parent is not None and parent.name == 'p' :
						found_p = True

				if in_p and not found_p :
					out_text += '</p>'
					in_p = False

				if s.name == 'p' :
					out_text += '<p>'
					in_p = True

				# link with content (image or text)
				elif s.name == 'a' and s.contents != None :

					# Get url from link
					if 'href' in s and self.domain not in s['href'] and s['href'] not in self.link_list :
						self.link_list.append(s['href'])

					# Explore content of <a/>
					global_s_content=''
					for s_content in s.contents :
						# image in link
						if s_content.name != None and 'img' in s_content.name :
							s_image = s_content['src']
							if s_image not in self.img_list and not s_image in self.image :
								self.img_list.append(s_image)
								global_s_content += str(s_content)

						# text in link
						elif s_content.name != None :
							s_text = utils.textutils.sanitizeText(self.service, str(s_content))
							global_s_content += self.internal_addTag(s_text)

					if global_s_content :
						out_text += '<a href="'+s['href']+'">'+global_s_content+'</a>'

				# Contains text (not comment) and parent is not a link
				# Normaly get <p>text</p> and text<br/> stuff
				elif s.name == None and s.parent.name != 'a' and not isinstance(s, Comment):
					s_content = str(s).strip()
					if len(s_content) > 0 :
						s_text = self.internal_addText(s_content)
						# if starts with letter, add space before.
						if len(s_text) > 0 and s_text[0].islower() :
							s_text = ' '+s_text

						s_text = utils.textutils.sanitizeText(self.service, s_text)
						out_text += self.internal_addTag(s_text)

				# img without associated link
				elif s.name == 'img' and s.parent.name != 'a' :
					s_image = s['src']
					#print("[img] {0} [/img] ".format(s_image))
					# if s_image not in self.img_list and not s_image in self.image and s_image.startswith('http'):
					if s_image not in self.img_list and not s_image in self.image :
						self.img_list.append(s_image)
						out_text += '<img src="'+s_image+'"/>'

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

				if not added_more and len(out_text) >= more_size :
					out_text += '<!--more-->'
					added_more = True

		# remove multiple spaces :
		out_text = re.sub(' +',' ',out_text)

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
			'list_images' : self.img_list,
			'list_links' : self.link_list,
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

		if len(self.img_list) > 0 :
			print(u'+---[{} images]'.format(len(self.img_list)))

		if len(self.link_list) > 0 :
			print(u'+---[{} links]'.format(len(self.link_list)))

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

	# add tags
	def internal_addTag(self,text) :
		for tag in self.tags :
			word_re = re.compile(r'\b{}\b'.format(tag), re.IGNORECASE)
			text = word_re.sub('<b>'+tag+'</b>',text)
		return text
