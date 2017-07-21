import os, sys, re, time
import traceback

import requests
import feedparser # read rss feed
import pickle # saving rss as links

from bs4 import BeautifulSoup # parse page
from urllib.parse import urlparse # parse url
from difflib import SequenceMatcher # for similarity

from nltk.probability import FreqDist
import utils.nltk_common as nltk_common

import utils
from beatcrunch import Article

headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'}

# Remove crappy suffixes
def sanitizeUrl(base,url) :

    # Relative url
    if url.startswith('/') :
        entry_parsed = urlparse(base)
        entry_domain = '{uri.scheme}://{uri.netloc}'.format(uri=entry_parsed)
        url = entry_domain+url
        #print(uurl)

    # Transform 443 style in https style
    if 'http://' in url and ':443' in url :
        url = re.sub('http://','https://',url)
        url = re.sub(':443','',url)
        # print(uurl)

    # find if this url is the final one
    try :
        r = requests.get(url)
        link = r.url
    except :
        print(u"+--[Error] Sanitize URL {}".format(url))
        print(u"Unexpected error : {}".format( sys.exc_info()))
        link = url
    # remove tracking crap
    link = link.rsplit('?', 1)[0]
    link = link.rsplit('#', 1)[0]
    return link

# Remove words from services rules
def sanitizeTitle(service, title) :
    if service.find('sanitize') is not None :
        for removedField in service.find('sanitize').findall("remove") :
            if removedField.get('type') == "title" :
                title = re.sub(removedField.text,'',title)

    # Remove non alphanumeric
    title = utils.utils.sanitizeText(title)

    #TODO : Remove emojis
    # remoji = re.compile(u'['
    # u'\U0001F300-\U0001F64F'
    # u'\U0001F680-\U0001F6FF'
    # u'\u2600-\u26FF\u2700-\u27BF]+',
    # re.UNICODE)
    # title = remoji.sub('',title)

    # title = re.sub('[«»]','',title)
    return title

#
def getRelatedService(services, name) :
    for s in services.findall('service') :
        if (s.find('id').text == name) :
            # print(u"+--[{}] service found".format(name))
            return s

    print(u"+--[Error] {} unknown".format(name))
    return None

def getRSSArticles(service, rss_url, oldlist) :
    articles = []
    feedlist = []

    rss_lang = service.get('lang')

    feed = feedparser.parse(rss_url)
    # print(u"+--[Got] {} rss articles (in {}ms)".format(len(feed.entries),int((time.time()-starttime)*1000.0)))

    starttime = time.time()
    for post in feed.entries:
        # Add to current json
        feedlist.append(post.link)

        # If new post, push it.
        if post.link not in oldlist :
            title = sanitizeTitle(service, post.title)
            link = sanitizeUrl(rss_url,post.link)
            try :
                a = Article.Article(service,title,link,rss_lang)
                articles.append(a)
            except :
                print(u"+--[Error {}] {} {} ".format(service,title,link))
                print(u"Unexpected error")

    return articles, feedlist


def getWebArticles(service,rss_url,oldlist) :
    articles = []
    feedlist = []

    rss_lang = service.get('lang')
    soup = getArticleContent(rss_url)

    # Get list of articles from container -->
    container_type = service.find('get').find('container').get('type')
    #name = service.find('get').find('container').get('name')
    container_value = service.find('get').find('container').text

    text_container=soup.find(container_type, class_=container_value)

    if text_container is not None :
        # print(utext_container)
        item_type = service.find('get').find('item').get('type')
        item_value = service.find('get').find('item').text

        for t in text_container.find_all(item_type, class_=item_value) :
            # Get title
            title_type = service.find('get').find('title').get('type')
            title_value = service.find('get').find('title').text

            title = t.find(title_type, class_=title_value).text

            # Get article link
            link_type = service.find('get').find('link').get('type')
            link_value = service.find('get').find('link').text
            link_section = service.find('get').find('link').get('section')
            link_attribute = service.find('get').find('link').get('attribute')

            link = t.find(link_type, class_=link_value).find(link_section).get(link_attribute)

            # Add to current json
            feedlist.append(link)

            # If new post, push it.
            if link not in oldlist :
                link = sanitizeUrl(rss_url,link)
                title = sanitizeTitle(service, title)
                try :
                    a = Article.Article(service,title,link,rss_lang)
                    articles.append(a)
                except :
                    print(u"+--[Error {}] {} {} ".format(service,title,link))
                    print(u"Unexpected error")
    return articles, feedlist

# Get new articles from a live feed
def getNewArticles(service,settings) :
    # starttime = time.time()

    out_dir = settings.find('settings').find('output').text
    if not os.path.exists(out_dir+'/rss'): os.makedirs(out_dir+'/rss')

    rss_id = service.find('id').text
    rss_lang = service.get('lang')
    rss_feed = out_dir+'/rss/'+rss_lang+'-'+rss_id+'.list'

    rss_url = service.find('url').text
    url_type = service.find('url').get('type')

    # Load previous list
    if os.path.exists(rss_feed):
        with open (rss_feed, 'rb') as fp:
            oldlist = pickle.load(fp)
        # print(u"+--[Previous] {} articles loaded".format(len(oldlist)))
        if len(oldlist) == 0 :
            print(u"+--[WARNING] Feed seems down (update url ?)")

        # print(u"+--[Existing feed {}] with {} articles".format(rss_feed.encode('utf-8'),len(oldlist)))
    else :
        print(u"+--[New feed {}]".format(rss_feed.encode('utf-8')))
        oldlist = []

    # for o in oldlist :
    #     print(o.encode('utf-8'))

    articles = []
    feedlist = []

    # Parse rss feed
    try :
        if url_type == "rss" :
            articles, feedlist = getRSSArticles(service,rss_url, oldlist)
        elif url_type == "web" :
            articles, feedlist = getWebArticles(service,rss_url, oldlist)
            # elif url_type == "json" :
            #     feed = utils.utils.loadjson(rss_url)
    except :
        print(u"Unexpected error")
        traceback.print_exc()

    # RSS : Verify if we don't get crap (null file or smaller)
    if len(feedlist) < len(oldlist) :
        for l in oldlist :
            if l not in feedlist :
                feedlist.append(l)

    # Save RSS feed entries
    with open(rss_feed, 'wb') as fp:
        pickle.dump(feedlist, fp)

    # Return new articles with names
    return articles

# Get Page content and return parsed page.
def getArticleContent(url) :
    web_page = requests.get(url, headers=headers, allow_redirects=True)

    return BeautifulSoup(web_page.content, "html.parser")

# For twitter
def getImageData(url) :
    response = requests.get(url, headers=headers, allow_redirects=True)
    return response.content

# Allow pages from selected category
def allowArticleCategory(service,article) :
    if service.find('selection') is not None :
        for sel in service.find('selection').findall("select") :
            sel_type = sel.get('type')
            sel_value = sel.get('value')
            sel_filter = sel.text  # text to match
            # print(uarticle.url)
            # print(usel_filter)
            if (sel_type == "url") and (sel_filter in article.url) :
                return True
            elif (sel_type == "div") :
                sel_section = sel.get('section')
                soup = getArticleContent(article.url)
                text_sec=soup.find(sel_type, class_=sel_value)
                #print(utext_sec)
                if text_sec is not None :
                    for t in text_sec.find_all(sel_section):
                        if sel_filter in t :
                            return True
        # No match, no game.
        return False
    else :
        # No selection category for this source
        return True

def detectAdArticle(service,article) :
    if service.find('filters') is not None :
        for filter in service.find('filters').findall("filter") :
            filter_type = filter.get('type')
            filter_value = filter.text

            # filter based on url
            if filter_type == "url" and filter_value in article.url :
                print(u"+---[Filter] Url matched on {} ".format(filter_value.encode('utf8')))
                return True

            # based on title
            if filter_type == "title" and filter_value in article.title.lower() :
                print(u"+---[Filter] Title matched on {} ".format(filter_value.encode('utf8')))
                return True
			# based on content
            if filter_type == "class" :
                filter_name = filter.get('name')
                filter_section = filter.get('section')
                #print(ufilter_name)

                f=article.soup.find(filter_section, class_=filter_name)
                if f is not None and filter_value in f.get_text().lower() :
                    print(u"+---[Filter] Content matched on {} ".format(filter_value.encode('utf8')))
                    return True
    return False

# Get similarity between two lists of tags (blanks are junk)
def similar(a, b):
    return SequenceMatcher(lambda x: x == " ", a, b).ratio()

def extendedSimilar(a, b):
    aL=a.split()
    bL=b.split()

    #TODO Calcul de moyenne pondérée
    # Plus la note mot est élevée tot, plus le poids est fort
    maxSim=0

    for i in range(1,min(len(aL),len(bL))) :
        aX = ' '.join(aL[:i])
        bX = ' '.join(bL[:i])
        g = similar(aX,bX)

        # Si g est grand (sup à 0.6) entre 4 et 6 on a de bonne chances que ce soit un duplicat
        # Dans ce cas, on renvoie cette valeur.
        if 4 <= i <= 6 :
            if g > 0.6 :
                print(u"+---- {0:.2f} [{1}] [{2}]".format(g,aX.encode('utf8'),bX.encode('utf8')))
            if g > maxSim :
                maxSim = g

    return max(maxSim,g)

# Detect if keywords or title from articles are already somewhere
# 5 keywords minimum
def detectSimArticle(service,article,sim_dict) :
    tags = ' '.join(article.tags)
    maxsim=0

    for key, value in sim_dict.items():
        # Test Key (tags) if enough
        if len(article.tags) >= 4 :
            s = similar(tags,key)
            if s > maxsim :
                maxsim = s
                maxsimwith = key

    #TODO adapt after learning
    # if maxsim > 0.4 :
    #     # print(u"+--[Tag]      [{}]".format(tags))
    #     print(u"+---[Sim] {0:.2f} [{1}]".format(maxsim,sim_dict[maxsimwith].encode('utf8')))
    #     print(u"+---[Sim]      [{}]".format(maxsimwith.encode('utf8')))
        # print(u"+--[Match]     [{}]".format(maxsimwith))

    #TODO mettre plus de poids sur les premiers mots
    if maxsim > 0.4 :
        maxsim = extendedSimilar(tags,maxsimwith)
        # print(u"+---[MaxSim] {0:.2f}".format(maxsim))
    # else :
        # print(u"+---[NoSim] {0:.2f}".format(maxsim))

    if maxsim > 0 :
        return maxsim,sim_dict[maxsimwith]
    else :
        return 0,""

# Detect if article is slighly the same as another already published
def detectSimArticleTitle(title,title_dict) :
    maxsim = 0
    maxsimwith =""

    for t in title_dict :
        g = similar(title,t)
        if g > maxsim :
            maxsim = g
            maxsimwith = t

    if maxsim > 0 :
        return maxsim,maxsimwith
    else :
        return 0,""

def rateArticle(service,article,sim_dict) :
    # print(u"+-[Rate] {} ".format(article.title))
    if not allowArticleCategory(service,article) :
        print(u"+---[Rate] Category not allowed")
        return 0
    elif detectAdArticle(service,article) :
        print(u"+---[Rate] Advert found")
        return 0
    else :
        return 1

# Get 10 mosts common tags
def tagsTrend(articles) :
    taglist = []
    for article in articles :
        for tag in article.tags :
            taglist.append(tag)

    fdist = FreqDist(taglist)
    out = []
    for x in fdist.most_common(10) :
        out.append(x[0])

    return out

# Add MAX main tags to title
def addTagsToTitle(article,max) :
        nb=0
        text=article.title
        for w in text.split() :
            if nb >= max : return text
            if w.lower() in article.tags :
                text = re.sub(w,'#'+w.lower(),text)
            nb += 1

        return text
