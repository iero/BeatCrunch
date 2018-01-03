from nltk import RegexpTokenizer

# Common stopwords in french and english
def get_stopwords(lang) :
	stopset = []

	stopwords_ponctuation = [',','"',';',':','.','?','!','*','—']
	for w in stopwords_ponctuation: stopset.append(w)

	if lang == "fr" or lang == "all":
		stopwords_base = ['aussi','au','aux','avec','ça','ce','ces','dans','de','des','du','elle','en','et','eux','il','je','là','la','le','leur','leurs','lui','ma','mais','me','même','mes','moi','mon','ne','nos','notre','nous','on','ou','où','par','pas','pour','qu','que','qui','si','sa','se','ses','son','sur','ta','te','tes','toi','ton','tu','un','une','vos','votre','vous','ceci','cela','celà','cet','cette','ici','ils','les','leurs','quel','quels','quelle','quelles','sans','soi','tout','toutes','toute','tous']

		stopwords_lettres_seules = ['c','d','j','l','à','m','n','s','t','y',"c’","d’","j’","l’","m’","n’","s’","t’","qu’"]

		stopwords_verbeterne_etre = ['être','été','étée','étées','étés','étant','suis','es','est','sommes','êtes','sont','serai','seras','sera','serons','serez','seront','serais','serait','serions','seriez','seraient','étais','était','étions','étiez','étaient','fus','fut','fûmes','fûtes','furent','sois','soit','soyons','soyez','soient','fusse','fusses','fût','fussions','fussiez','fussent']
		stopwords_verbeterne_avoir = ['a','avoir','ayant','eu','eue','eues','eus','ai','as','avons','avez','ont','aurai','auras','aura','aurons','aurez','auront','aurais','aurait','aurions','auriez','auraient','avais','avait','avions','aviez','avaient','eut','eûmes','eûtes','eurent','aie','aies','ait','ayons','ayez','aient','eusse','eusses','eût','eussions','eussiez','eussent']

		for w in stopwords_base: stopset.append(w)
		for w in stopwords_lettres_seules: stopset.append(w)
		for w in stopwords_verbeterne_avoir: stopset.append(w)
		for w in stopwords_verbeterne_etre: stopset.append(w)

	if lang == "en" or lang == "all":
		stopwords_base = ['a','about','above','above','across','after','afterwards','again','against','all','almost','alone','along','already','also','although','always','among','amongst','amoungst','amount','and','another','any','anyhow','anyone','anything','anyway','anywhere','are','around','as','at','back','because','before','beforehand','behind','below','beside','besides','between','beyond','bill','both','bottom','but','by','co','con','de','describe','detail','do','done','down','due','during','each','eg','eight','either','else','elsewhere','empty','enough','etc','even','ever','every','everyone','everything','everywhere','except','few','fire','for','former','formerly','from','front','full','further','he','hence','her','here','hereafter','hereby','herein','hereupon','hers','herself','him','himself','his','how','however','hundred','i','if','in','inc','indeed','interest','into','it','its','itself','last','latter','latterly','least','less','ltd','many','me','meanwhile','mill','mine','more','moreover','most','mostly','much','must','my','myself','name','namely','neither','never','nevertheless','next','no','nobody','none','nor','not','nothing','now','nowhere','of','off','often','on','once','only','onto','or','other','others','otherwise','our','ours','ourselves','out','over','own','part','per','perhaps','please','rather','re','same','serious','several','she','side','since','sincere','so','some','somehow','someone','something','sometime','sometimes','somewhere','still','such','than','that','the','their','them','themselves','then','there','thereafter','thereby','therefore','therein','thereupon','these','they','thin','this','those','though','through','throughout','thru','thus','to','together','too','toward','towards','under','until','upon','us','very','via','we','well','were','what','whatever','when','whence','whenever','where','whereafter','whereas','whereby','wherein','whereupon','wherever','whether','which','while','whither','who','whoever','whole','whom','whose','why','with','within','without','yet','you','your','yours','yourself','yourselves','the']

		stopwords_verbs = ['am','be','became','become','becomes','becoming','been','being','call','can','cannot','cant','could','couldnt','cry','fill','find','found','get','give','go','had','has','hasnt','have','is','keep','made','may','might','move','say','says','see','seem','seemed','seeming','seems','should','show','take','put','was','will','would']

		for w in stopwords_base: stopset.append(w)
		for w in stopwords_verbs: stopset.append(w)

	return stopset

# Clean text or sentence, removing stopwords
# return list
def nlp_clean(data,stopwords):
	new_str = data.lower()
	tokenizer = RegexpTokenizer(r'\w+')
	dlist = tokenizer.tokenize(new_str)
	for a in dlist :
		if len(a) < 2 :
			dlist.remove(a)
	cleanList = [word for word in dlist if word not in stopwords]
	return cleanList
