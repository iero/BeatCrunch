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

import utils
import Statistics
import Article

if __name__ == "__main__":

    if len(sys.argv) < 3 :
        print(u"Please use # python beatcrunch.py settings.xml services.xml")
        sys.exit(1)
    else :
        settings = utils.utils.loadxml(sys.argv[1])
        services = utils.utils.loadxml(sys.argv[2])

        out_dir = settings.find('settings').find('output').text
        if not os.path.exists(out_dir): os.makedirs(out_dir)
        if not os.path.exists(out_dir+'/json'): os.makedirs(out_dir+'/json')

        if settings.find('settings').find('debug').text == "True" :
            debug=True
            print(u"+-[Debug] ON")
        else :
            debug=False
            print(u"+-[Debug] OFF")

        if settings.find('settings').find('shorten').text == "True" :
            shorten=True
            print(u"+-[Shorten] ON")
        else :
            shorten=False
            print(u"+-[Shorten] OFF")

        if settings.find('settings').find('twitter').text == "True" :
            twitter=True
            print(u"+-[Twitter] ON")
        else :
            twitter=False
            print(u"+-[Twitter] OFF")

        if settings.find('settings').find('mastodon').text == "True" :
            mastodon=True
            print(u"+-[Mastodon] ON")
        else :
            mastodon=False
            print(u"+-[Mastodon] OFF")


    # JSON feed for today
    today_json_file=out_dir+'/json/'+time.strftime("%Y%m%d")+".json"
    json_today = utils.utils.loadjson(today_json_file)
    if debug : print(u"+-[Loading] [{}]".format(today_json_file.encode('utf-8')))

    # Load statistics for today
    statistics = Statistics.Statistics(json_today)
    json_today["statistics"] = []
    json_today["statistics"].append(statistics.printJson())

    # Create dictionnary & index for similarity
    sim_dict = utils.utils.getLastDaysTags(settings,5)

    if debug : print(u"+-[Loading] {} articles for similarity".format(len(sim_dict)))

    # Get new articles for each selected service
    for s in settings.find('settings').find("services").findall('service'):
        service = utils.services.getRelatedService(services,s.text)

        if debug : print(u"+-[Service] [{}]".format(s.text.encode('utf-8')))
        # Get new articles
        articles = utils.services.getNewArticles(service, settings)

        if debug and len(articles) > 0 :
            print(u"+--[New] {} articles to crunch".format(len(articles)))
            print(u"+-------------------------")

        for article in articles :
            statistics.total += 1
            article.show()

            # Test if article is interesting
            article.rate  = utils.services.rateArticle(service,article,sim_dict)

            # Detect if already published
            article.similarity, article.similarity_with = utils.services.detectSimArticle(service,article,sim_dict)

            # Add this article in comparaison table if more than 5 tags
            if len(article.tags) >= 5 :
                tags = ' '.join(article.tags)
                sim_dict[tags] = article.title

            if article.rate == 0 :
                statistics.filtered += 1
            elif article.similarity >= 0.6 :
                statistics.duplicates += 1
            else :
                statistics.nbtags += len(article.tags)
                statistics.nbwords += len(article.text)

                # shorten url
                if shorten:
                    article.shorturl = utils.utils.shortenLink(settings,article.url)

                # Prepare and send tweet
                if twitter :
                    if (utils.share.tweet(settings,article)) :
                        statistics.twitted += 1

                # Prepare and send toot
                if mastodon :
                    if (utils.share.toot(settings,article)) :
                        statistics.tooted += 1

            print(u"+-------------------------")

            json_today[article.id] = []
            json_today[article.id].append(article.printJson())

    # Save today feed
    statistics.top_trend = utils.utils.tagsTrend(json_today,50)

    json_today["statistics"] = statistics.printJson()
    statistics.show()

    print(u"+-[done]")
    with open(today_json_file, 'w') as jsonfile:
        json.dump(json_today, jsonfile)
