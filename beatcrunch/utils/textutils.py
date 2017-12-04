import re

def parseURLName(url) :
	entry_parsed = urlparse(post.link)
	entry_domain = '{uri.scheme}://{uri.netloc}/'.format(uri=entry_parsed)
	entry = post.link.replace(entry_domain,"").replace('/','-').strip("-")
	entry = entry+".txt"
	return entry

def sanitizeText(service, text) :

	if text is None : return ''

	# Remove first and last spaces
	text = text.strip()

	# print(u"input [{}]".format(text))
	text = text.replace("\n", "")
	text = text.replace("\r", "")
	text = text.replace("\t", "")
	text = re.sub(r' {2,}',' ',text)
	# print(u"output [{}]".format(text))

	if len(text)==1 : return ''

	# General
	filtered_words=["adsbygoogle"]
	if any(x in text for x in filtered_words):
		text = ""

	# specific
	if service.find('sanitize') is not None :
		for removedField in service.find('sanitize').findall("remove") :
			if removedField.get('type') == "text" :
				if removedField.text.lower() in text.lower() :
					text = ""
	return text

