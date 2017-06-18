import os, re
import requests

from bs4 import BeautifulSoup # parse page
import feedparser # read rss feed
from urllib.parse import urlparse # parse url

import pickle # saving rss as links

from nltk.probability import FreqDist

import utils
from beatcrunch import Article

headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'}

# Remove crappy suffixes
def sanitizeUrl(url) :
    link = url.rsplit('?', 1)[0]
    link = link.rsplit('#', 1)[0]
    return link

# Remove words from services rules
def sanitizeTitle(service, title) :
    if service.find('sanitize') is not None :
        for removedField in service.find('sanitize').findall("remove") :
            if removedField.get('type') == "title" :
                title = re.sub(removedField.text,'',title)
    return title

def getRelatedService(services, name) :
    for s in services.findall('service') :
        if (s.find('id').text == name) : return s
    return None

# Get new articles from a live feed
#TODO : Add no RSS entry

def getNewArticles(service,settings) :
    out_dir = settings.find('settings').find('output').text
    if not os.path.exists(out_dir+'/rss'): os.makedirs(out_dir+'/rss')

    articles = []
    rss_id = service.find('id').text
    rss_lang = service.get('lang')
    rss_feed = out_dir+'/rss/'+rss_lang+'-'+rss_id+'.list'
    rss_url = service.find('url').text
    url_type = service.find('url').get('type')

    # Load previous list
    if os.path.exists(rss_feed):
        with open (rss_feed, 'rb') as fp:
            oldlist = pickle.load(fp)
    else :
        oldlist = []

    # new list
    feedlist=[]

    # Parse rss feed
    if url_type == "rss" :
        feed = feedparser.parse(rss_url)
        for post in feed.entries:
            link = sanitizeUrl(post.link)
            title = sanitizeTitle(service, post.title)
            # Add to current json
            feedlist.append(link)
            # If new post, push it.
            if link not in oldlist :
                try :
                    a = Article.Article(service,title,link,rss_lang)
                    articles.append(a)
                except :
                    print("[Error {}] {} {} ".format(service,title,link))

    elif url_type == "json" :
        feed = utils.utils.loadjson(rss_url)

    elif url_type == "web" :
        container_type = service.find('get').find('container').get('type')
        #name = service.find('get').find('container').get('name')
        container_value = service.find('get').find('container').text

        item_type = service.find('get').find('item').get('type')
        item_value = service.find('get').find('item').text

        link_type = service.find('get').find('link').get('type')
        link_name = service.find('get').find('link').get('name')
        text_type = service.find('get').find('item').get('type')

        soup = getArticleContent(rss_url)
        text_container=soup.find(container_type, class_=container_value)
        if text_container is not None :
#            print(text_container)
            for t in text_container.find_all(item_type, class_=item_value) :
                print(t)
                link = t.get("href")
                title = t.get("title")
                print(link)
                print(title)
                link = sanitizeUrl(link)
                title = sanitizeTitle(service, title)

                if link.startswith('/') :
                    entry_parsed = urlparse(rss_url)
                    entry_domain = '{uri.scheme}://{uri.netloc}'.format(uri=entry_parsed)
                    link = entry_domain+link
                    #print(link)

                    # Add to current json
                    feedlist.append(link)
                    # If new post, push it.
                    if link not in oldlist :
                        a = Article.Article(service,title,link,rss_lang)
                        articles.append(a)

    # Save RSS feed entries
    with open(rss_feed, 'wb') as fp:
        pickle.dump(feedlist, fp)

    # Return new articles with names
    return articles

# Get Page content and return parsed page.
def getArticleContent(url) :
    web_page = requests.get(url, headers=headers, allow_redirects=True)
    #TODO : handle multiple redirection
    if web_page.history :
        link = sanitizeUrl(web_page.url)
        web_page = requests.get(link, headers=headers)

    # Parse page
    return BeautifulSoup(web_page.content, "html.parser")

# Allow pages from selected category
def allowArticleCategory(service,article) :
    if service.find('selection') is not None :
        for sel in service.find('selection').findall("select") :
            sel_type = sel.get('type')
            sel_value = sel.get('value')
            sel_filter = sel.text

            #print("+-[CatFilter] [{}] {}".format(sel_type.encode('utf-8'),sel_filter.encode('utf-8')))
            if (sel_type == "url") and (sel_value in article.url) :
                return True
            elif (sel_type == "div") :
                sel_section = sel.get('section')
                soup = getArticleContent(article.url)
                text_sec=soup.find(sel_type, class_=sel_value)
                #print(text_sec)
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
                print("+-[Url filter] matched on "+filter_value)
                return True
                # based on title
            if filter_type == "title" and filter_value in article.title.lower() :
                print("+-[Title filter] matched on "+filter_value)
                return True
			# based on content
            if filter_type == "class" :
                filter_name = filter.get('name')
                filter_section = filter.get('section')
                #print(filter_name)

                f=article.soup.find(filter_section, class_=filter_name)
                if f is not None and filter_value in f.get_text().lower() :
                    print("+-[Content filter] matched on "+filter_value)
                    return True
    return False

    #Filters title
def detectTitleFilter(service,article) :
    if service.find('filters') is not None :
        for filter in service.find('filters').findall("filter") :
            filter_type = filter.get('type')
            filter_value = filter.text
            filter_result = article.soup.find(filter_type, class_=filter_value)
            if filter_result is not None :
                print("+-[Content filter] matched on "+filter_value)
                return True
    return False

def rateArticle(service,article) :
    print("+-[Test] Title : {} ".format(article.title))
    if not allowArticleCategory(service,article) :
        print("Category not allowed")
        return 0
    if detectAdArticle(service,article) :
        print("Advert found")
        return 0
    if detectTitleFilter(service,article) :
        print("Title crap found")
        return 0

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
