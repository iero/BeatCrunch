import os, time, re
import json

import xml.etree.ElementTree as ET

from datetime import datetime, timedelta

from urllib.parse import urlparse
from nltk.probability import FreqDist

from pyshorteners import Shortener # for bitly


# Tweet sizes = add 1 for extra space
tweet_size = 140
tweet_link_size = 1+23

def isInt(s):
    try:
        int(s)
        return True
    except ValueError:
        return False

def loadxml(params_file) :
    tree = ET.parse(params_file)
    return tree.getroot()

def loadjson(json_file) :
    if os.path.exists(json_file) :
        with open(json_file) as f:
            return json.load(f)
    else :
        return {}

def printjsonTitles(json_data) :
    for news in json_data :
        for t in json_data[news] :
            print(ut['title'])

# Use Bitly
def shortenLink(s,url) :
    try :
        for service in s.findall('service') :
            if service.get("name") == "bitly" :
                sh = Shortener('Bitly',bitly_token=service.find("token").text)
                return sh.short(url)
        # If service not found
        return url
    except :
            return url

# Sanitize text to remove crapy thing and make it readable
#TODO : Maybe a library will do it ?

def sanitizeText(text) :

    # Remove first and last spaces
    text = text.strip()

    # print(u"input [{}]".format(text))
    text = text.replace("\n", "")
    text = text.replace("\r", "")
    text = text.replace("\t", "")
    text = re.sub(r' {2,}',' ',text)
    # print(u"output [{}]".format(text))

    if len(text)==1 : return ""
    else : return text

def getLastDaysTitles(settings,nbdays) :
    title_dict = []
    out_dir = settings.find('settings').find('output').text

    for days in range(0,nbdays) :
        d = datetime.today() - timedelta(days=days)
        json_file=out_dir+'/json/'+d.strftime("%Y%m%d")+".json"
        #print(ujson_file)

        if os.path.exists(json_file):
            j = loadjson(json_file)
            for news in j :
                if news != "statistics" :
                    for t in j[news] :
                        title_dict.append(t['title'])

    return title_dict

# Get dictionary (and index to titles) of articles from the last 5 days with 5+ keywords
def getLastDaysTags(settings,nbdays) :
    similarity_dict = {}

    out_dir = settings.find('settings').find('output').text

    for days in range(0,nbdays) :
        d = datetime.today() - timedelta(days=days)
        json_file=out_dir+'/json/'+d.strftime("%Y%m%d")+".json"

        if os.path.exists(json_file):
            j = loadjson(json_file)
            # print(u"{} articles".format(len(j)-1))
            for news in j :
                if news != "statistics" :
                    for t in j[news] :
                        # print(t['tags'])
                        if len(t['tags']) >= 4 :
                            tags = ' '.join(t['tags'])
                            # print(utags)
                            similarity_dict[tags] = t['title']
        # print(u"Loading {} : {} articles".format(json_file,len(similarity_dict)))

    return similarity_dict

# Find Text in Titles
def findTitlefromText(json_data,text) :
    articles = []
    for news in json_data :
        if news != "statistics" :
            for t in json_data[news] :
                if text in t['title'].lower() :
                    articles.append(t['title'])
    return articles


# Find Text in Articles content
def findArticlefromText(json_data,text) :
    articles = []
    for news in json_data :
        if news != "statistics" :
            for t in json_data[news] :
                if text in t['text'].lower() :
                    articles.append(t['title'])
    return articles

# Get 'number' mosts common tags statistics json file
def tagsTrend(json_data,number) :
    taglist = []
    for item in json_data :
        if item != "statistics" :
            for t in json_data[item] :
                for tag in t['tags'] :
                    taglist.append(tag)

    #TODO : USE similarity.findTags instead
    fdist = FreqDist(taglist)
    out = []
    for x in fdist.most_common(number) :
        if len(x[0])>1 :
            out.append(x[0])

    return out

def isTrendyTag(tag,json) :
    for service in json.find('hashtags') :
        for t in service.find('hashtags').findall("tag") :
            print(uservice.get("value"))
            if service.get("value") == tag :
                print(u"TAG : "+tag)
                return True

def cleanImage_url(page,img) :
    if img and not img.startswith("data:") :
        if img.startswith("//") :
            img = "https:"+out_img
        elif img.startswith("/") :
            parsed_web_page = urlparse(page.url)
            dom =  '{uri.scheme}://{uri.netloc}/'.format(uri=parsed_web_page)
            img = dom+img

        return img
    else :
        return None

# Replace Tags with #tags in given text
def addTagsToTitle(title,tags) :
    for w in title.split(" ") :
        for x in tags :
            if x[1] > 1 and x[0] == w.lower() :
                title = title.replace(w,"#"+x[0])
    return title

def cleanClickBait(title) :
    # Remove "* 5 nouveaux *"
    # Les 5 infos tech
    # 3 livres
    # Facebook : 5 erreurs
    # verbes en ez

    #TODO : remove first spaces when recording !!
    sTitle = title.split(" ")
    print(usTitle[0])
    print(usTitle[1])
    if isInt(sTitle[0]) and not isInt(sTitle[1]) :
        #TODO : replace first only
        title.replace(sTitle[0],"Des")
    return title
