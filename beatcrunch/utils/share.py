import os
import urllib.request as request

from PIL import Image # For converting image to PNG
from urllib.parse import urlparse
from os.path import splitext, basename

from TwitterAPI import TwitterAPI
from mastodon import Mastodon

import utils

def tweet(s,article) :
    # try :
    for service in s.findall('service') :
        if service.get("name") == "twitter" :
            t = TwitterAPI(consumer_key=service.find("consumer_key").text, consumer_secret=service.find("consumer_secret").text, access_token_key=service.find("access_token_key").text, access_token_secret=service.find("access_token_secret").text)

    text = article.getTweet()
    print(u"+---[Tweet] {}".format(text))


    if article.image :
        data = utils.services.getImageData(article.image)
        t.request('statuses/update_with_media', {'status':text}, {'media[]':data})
    else :
        t.request('statuses/update', {'status':text})

    # except:
    #     print(u"+---[Tweet] Fail")

def toot(s,article) :
    # try :
    for service in s.findall('service') :
        if service.get("name") == "mastodon" :
            m = Mastodon(client_id = service.find("client_service").text, client_secret = service.find("client_secret").text, access_token = service.find("access_token").text, api_base_url = service.find("server").text)

    text = article.getTweet()
    print(u"+---[Toot] {}".format(text))


    if article.image :
        # print("Converting image")
        disassembled = urlparse(article.image)
        img_name, img_ext = splitext(basename(disassembled.path))
        img_local = ("/tmp/"+img_name+img_ext)

        # try :
        request.urlretrieve(article.image, img_local)
        if "png" not in img_ext :
            img = Image.open(img_local)
            img_local = ("/tmp/"+img_name+".png")
            img.save("/tmp/"+img_name+".png",'png')
            os.remove("/tmp/"+img_name+img_ext)

        media_id = m.media_post(img_local)
        # print(media_id)

        m.status_post(text,in_reply_to_id=None,media_ids=[media_id])
        if os.path.exists(img_local) :
            os.remove(img_local)
        # except :
        #     m.toot(text)
    else :
        m.toot(text)
    # except:
    #     print(u"+---[Toot] Failed")
