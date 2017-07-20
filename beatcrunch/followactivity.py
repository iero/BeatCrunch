import sys,time
import json
import tweepy

import utils

import xml.etree.ElementTree as ET

def getActivity(s) :
    for service in s.findall('service') :
        if service.get("name") == "twitter" :
            username = service.find("username").text
            consumer_key=service.find("consumer_key").text
            consumer_secret=service.find("consumer_secret").text
            token_key=service.find("access_token_key").text
            token_secret=service.find("access_token_secret").text


    auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(token_key, token_secret)
    api = tweepy.API(auth)

    # Get last status
    json_home = {}

    for status in tweepy.Cursor(api.user_timeline, id=username).items(500):
        if status.favorite_count != 0 or status.retweet_count != 0 :
            json_home[status.id] = []
            json_home[status.id].append(status._json)

    return json_home


if __name__ == "__main__":

    if len(sys.argv) < 2 :
        print(u"Please use # python followactivity.py settings.xml")
        sys.exit(1)
    else :
        settings = utils.utils.loadxml(sys.argv[1])

    out_dir = settings.find('settings').find('output').text

    # JSON feed for today
    today_json_file=out_dir+'/json/'+time.strftime("%Y%m%d")+".json"
    json_today = utils.utils.loadjson(today_json_file)
    print(u"+-[Loading] [{}]".format(today_json_file.encode('utf-8')))

    activity = getActivity(settings)
    print(activity)
