from bs4 import BeautifulSoup # parse page


with open ("/Users/greg/Downloads/robot.html", 'rb') as source:
	soup = BeautifulSoup(source, "html.parser")
	section = soup.find('div', class_='articlebodyonly')

# Detect unnecessary tags and crappy attributes in original soup
	tags_to_keep = ['p','a','img','ul','li']
	tags_to_remove = []

	attributes_to_keep = ['src','href']
	attributes_to_remove = []

	for tag in section.find_all(True):
		# Tag
		if tag.name not in tags_to_keep and tag.name not in tags_to_remove :
			tags_to_remove.append(tag.name)

		# Attribute
		for attr in tag.attrs :
			if attr not in attributes_to_keep and attr not in attributes_to_remove :
				attributes_to_remove.append(attr)

	# Remove unnecessary tags but keep content
	print("+---[Remove tags] {}".format(','.join(tags_to_remove)))
	for tag in tags_to_remove :
		for t in section.find_all(tag) :
			t.replaceWithChildren()

	# Remove attributes
	print("+---[Remove attributes] {}".format(','.join(attributes_to_remove)))
	for attribute in attributes_to_remove :
		for tag in section.findAll():
			del(tag[attribute])

	out_text = ""
	# Remove tags without content
	for s in section.descendants :
		# text but parent is not a
		if s.name == None and s.parent.name != 'a':
			s_text = addText(str(s).strip())
			out_text += s_text
			print("[text] {1}".format(s_text))
		elif s.name == 'a' :
			print("[a {0}] {1} [/a] ".format(s['href'],s.contents[0]))
			# if not s.content[0]
			out_text += '<a href="'+s['href']+'">'+s.contents[0]+'</a>'
		elif s.name == 'img' :
			print("[img] {0} [/img] ".format(s['src']))
			out_text += '<img src="'+s['src']+'"/>'
		elif s.name != None :
			print("[{}]".format(s.name))

def addText(text) :
	if text == '' :
		return text

	if text[-1:] != ' ' :
		text += ' '
	if not text.startswith('<p>') and not text.endswith('</p>') :
		text = '<p>'+text+'</p>'

	return text
