# -*-coding:utf-8 -*
from __future__ import unicode_literals

import os, sys, socket, time
import re
import json
import pytz

import urllib3
import requests
import feedparser
import urllib.request as request

from os.path import splitext, basename

from bs4 import BeautifulSoup
from urllib.parse import urlparse
from feedgen.feed import FeedGenerator
from datetime import datetime
from pytz import timezone

import xml.etree.ElementTree as ET

from TwitterAPI import TwitterAPI
from pyshorteners import Shortener
from mastodon import Mastodon

import utils
import Statistics
import Article

import utils.tok as tok

BASE_DIR = os.path.dirname(os.path.dirname(__file__))

if __name__ == "__main__":

    tokenizer = tok.ToktokTokenizer()

    if len(sys.argv) < 3 :
        print("Please use # python beatstats.py settings.xml jsonfile")
        sys.exit(1)
    else :
        settings = utils.utils.loadxml(sys.argv[1])
        jsonfile = sys.argv[2]

        out_dir = settings.find('settings').find('output').text
        if not os.path.exists(out_dir): os.makedirs(out_dir)
        if not os.path.exists(out_dir+'/json'): os.makedirs(out_dir+'/json')

    # JSON feed for today
#    today_json_file=out_dir+'/json/'+time.strftime("%Y%m%d")+".json"
    json_today = utils.utils.loadjson(jsonfile)
    print("+-[Loading] [{}]".format(jsonfile.encode('utf-8')))

    # Load statistics for today
    statistics = Statistics.Statistics(json_today)
    json_today["statistics"] = []
    json_today["statistics"].append(statistics.printJson())

    statistics.show()

    # Extract tags from content
    alltags=[]

    artnb=0
    artmin=25
    artmax=100
    for article in json_today :
        artnb += 1

        if article == "statistics" : continue
        if artnb-1 < artmin : continue
        if artnb-1 >= artmax : break

        t = json_today[article][0]
        # print(t)
        print("[article {}]".format(artnb-1))
        # print("[article {}] {}".format(artnb-1,t['title']))
        # print("[article {}] {} words from {} in {}".format(artnb-1,t['text_size'],t['source'],t['lang']))

        # print(tokenizer.sanitizeText(t['text']))
        tags = utils.similarity.findTags(t['text'],t['lang'],10)

        title = utils.utils.addTagsToTitle(t['title'],tags)
        title = utils.utils.cleanClickBait(title)
        print("[article {}] {}".format(artnb-1,title))

        print("[article {}] Tags {}".format(artnb-1,tags))
        # print(tags)

        # check tags for similarity
        if len(tags) :
            taglist=""
            for x in tags :
                if len(x[0])>1 and x[1] > 1 :
                    taglist += x[0] +" "
            # 5+ tags to be defined as a sentence
            if len(taglist) >= 5 :
                alltags.append(taglist)
                print("[article {}] Tags added".format(artnb-1))
                # print("[article {}] Main tags :{}".format(artnb-1,taglist))

                # Compare when more than 2 entries..
                if len(alltags)> 2 :
                    sim_results = utils.similarity.find_similar(alltags)
                    if sim_results[0][1]>0 :
                        print(sim_results)
