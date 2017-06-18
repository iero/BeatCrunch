import os, time
import json

import xml.etree.ElementTree as ET

from datetime import datetime, timedelta

from urllib.parse import urlparse
from nltk.probability import FreqDist

# Tweet sizes = add 1 for extra space
tweet_size = 140
tweet_link_size = 1+23

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
            print(t['title'])

def sanitizeText(text) :
	filtered_words=["adsbygoogle","toto","Read next:"]
	if any(x in text for x in filtered_words):
		return ""
	else :
		return text.replace(r'\r','')

def getLastDaysTitles(settings,nbdays) :
    title_dict = []
    out_dir = settings.find('settings').find('output').text

    for days in range(0,nbdays) :
        d = datetime.today() - timedelta(days=days)
        json_file=out_dir+'/json/'+d.strftime("%Y%m%d")+".json"
        #print(json_file)

        if os.path.exists(json_file):
            j = loadjson(json_file)
            for news in j :
                if news != "statistics" :
                    for t in j[news] :
                        title_dict.append(t['title'])

    return title_dict

def findArticlefromText(json_data,text) :
    for news in json_data :
    	for t in json_data[news] :
            if text in t['text'] :
                return t['title']

# Get 10 mosts common tags statistics json file
def tagsTrend(json_data) :
    taglist = []
    for item in json_data :
        if item != "statistics" :
            for t in json_data[item] :
                for tag in t['tags'] :
                    taglist.append(tag)

    fdist = FreqDist(taglist)
    out = []
    for x in fdist.most_common(10) :
        out.append(x[0])

    return out

def isTrendyTag(tag,json) :
    for service in json.find('hashtags') :
        for t in service.find('hashtags').findall("tag") :
            print(service.get("value"))
            if service.get("value") == tag :
                print("TAG : "+tag)
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
