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

if __name__ == "__main__":

    if len(sys.argv) < 3 :
        print("Please use # python beatcrunch.py settings.xml services.xml")
        sys.exit(1)
    else :
        settings = utils.utils.loadxml(sys.argv[1])
        services = utils.utils.loadxml(sys.argv[2])

        out_dir = settings.find('settings').find('output').text
        if not os.path.exists(out_dir): os.makedirs(out_dir)
        if not os.path.exists(out_dir+'/json'): os.makedirs(out_dir+'/json')

        debug = settings.find('settings').find('debug').text
        if debug : print("+-[Debug ON]")

    # JSON feed for today
    today_json_file=out_dir+'/json/'+time.strftime("%Y%m%d")+".json"
    json_today = utils.utils.loadjson(today_json_file)
    if debug : print("+-[Loading] [{}]".format(today_json_file.encode('utf-8')))

    # Load statistics for today
    statistics = Statistics.Statistics(json_today)
    json_today["statistics"] = []
    json_today["statistics"].append(statistics.printJson())

    # Create dictionnary for similarity
    title_dict = utils.utils.getLastDaysTitles(settings,5)
    if debug : print("+-[Loading] {} articles for similarity".format(len(title_dict)))

    # Get new articles for each selected service
    for s in settings.find('settings').find("services").findall('service'):
        service = utils.services.getRelatedService(services,s.text)

        if debug : print("+-[Service] [{}]".format(s.text.encode('utf-8')))
        # Get new articles
        articles = utils.services.getNewArticles(service, settings)


        for article in articles :
            statistics.total += 1

            # Test if article is crappy
            article.rate  = utils.services.rateArticle(service,article)
            if (article.rate == 0) :
                statistics.filtered += 1
            else :
                # Add similarity
                title_dict.append(article.title)
                sim_results = utils.similarity.find_similar(title_dict)

                article.similarity=float("{0:.2f}".format(sim_results[0][1]))
                if article.similarity == 0 :
                    article.similarity_with=""
                else :
                    article.similarity_with = sim_results[0][2]

                # print("+--[Similarity] {0:.2f}".format(article.similarity))

                grade_treshold=float(settings.find('settings').find('similarity_min').text)
                if article.similarity >= grade_treshold :
                    statistics.duplicates +=1
                    print("+--[Duplicate] {0:.2f} with {1}".format(article.similarity,article.similarity_with))
                else :
                    print("+--[New] {}".format(article.similarity))
                    #tweet
                    #toot
                    #time.sleep(5)

            json_today[article.id] = []
            json_today[article.id].append(article.printJson())

    # Save today feed
    statistics.tags_trend = utils.utils.tagsTrend(json_today,10)
    print(statistics.tags_trend)

    json_today["statistics"] = statistics.printJson()

    with open(today_json_file, 'w') as jsonfile:
        json.dump(json_today, jsonfile)
