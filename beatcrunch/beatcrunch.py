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

        # Load general settings
        debug = utils.utils.loadSetting(settings,'debug')
        shorten = utils.utils.loadSetting(settings,'shorten')
        twitter = utils.utils.loadSetting(settings,'twitter')
        mastodon = utils.utils.loadSetting(settings,'mastodon')

    # JSON feed for today
    today_json_file=out_dir+'/json/'+time.strftime("%Y%m%d")+".json"
    json_today = utils.utils.loadjson(today_json_file)
    if debug :
        print(u"+-[Loading] {} articles from [{}]".format(len(json_today),today_json_file.encode('utf-8')))

    # Load statistics for today
    statistics = Statistics.Statistics(json_today)
    json_today["statistics"] = []
    json_today["statistics"].append(statistics.printJson())

    # Create dictionnary & index for similarity
    sim_dict = utils.utils.getLastDaysTags(settings,5)
    title_dict = utils.utils.getLastDaysTitles(settings,5)
    if debug :
        print(u"+-[Loading] {} articles for similarity based on tags".format(len(sim_dict)))
        print(u"+-[Loading] {} articles for similarity based on titles".format(len(title_dict)))

    # Get new articles for each selected service
    for s in settings.find('settings').find("services").findall('service'):
        service = utils.services.getRelatedService(services,s.text)

        if debug :
            if service is None :
                print(u"+-[Service] Error {} unknown service !".format(s.text))
            else :
                print(u"+-[Service] [{}]".format(service.find('id').text.encode('utf-8')))

        # Get new articles
        articles = utils.services.getNewArticles(service, settings, 0)

        if debug and len(articles) > 0 :
            print(u"+--[New] {} articles to crunch".format(len(articles)))
            print(u"+-------------------------")

        for article in articles :
            statistics.total += 1
            article.show()

            # Test if article is interesting
            article.rate  = utils.services.rateArticle(service,article)

            # Detect if already published based on tags
            tags_sim, tags_sim_with = utils.services.detectSimArticle(service,article,sim_dict)

            # Add this article in comparaison table if more than 5 tags
            if len(article.tags) >= 5 :
                tags = ' '.join(article.tags)
                sim_dict[tags] = article.title

            # Find if really new based on title
            title_sim, title_sim_with = utils.services.detectSimArticleTitle(article.title,title_dict)
            title_dict.append(article.title)

            # If a title is more than 80% common with another one..
            # it might be the same article !
            if title_sim > tags_sim and title_sim > 0.8 :
                print(u"+---[Sim Title] of {0:.2f} with [{1}]".format(title_sim,title_sim_with.encode('utf8')))
                article.similarity = title_sim
                article.similarity_with = title_sim_with
            else :
                print(u"+---[Sim Tags] of {0:.2f} with [{1}]".format(tags_sim,tags_sim_with.encode('utf8')))
                article.similarity = tags_sim
                article.similarity_with = tags_sim_with

            if article.rate == 0 :
                statistics.filtered += 1
            elif article.similarity >= 0.6 :
                statistics.duplicates += 1
            else :
                statistics.nbtags += len(article.tags)
                statistics.nbwords += len(article.text)

                # Never tweet 2 times the same thing
                # utils.utils.verifyLink(article.url)

                # Verify that we will not flood (more than 3 articles)
                if len(articles) > 3 :
                    print(u"+--[ALERT] {} articles to push.. STOP".format(len(articles)))
                    break

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
