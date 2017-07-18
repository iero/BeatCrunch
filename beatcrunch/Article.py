import time
import re
import pytz

from datetime import datetime
from urllib.parse import urlparse

import utils

current_milli_time = lambda: int(round(time.time() * 1000))

class Article:
    nbarticles = 0

    def __init__(self, service, title, url, lang):
        # startime = time.time()

        self.service_name = service.find('id').text
        self.service_mention = service.find('mention').text

        self.id = str(current_milli_time())
        self.service = service
        self.title = title
        self.lang = lang
        self.date = datetime.now(pytz.timezone('Europe/Paris')).isoformat(),

        self.url = url
        self.shorturl = url

        self.soup = utils.services.getArticleContent(self.url)
        # print(self.soup)

        self.image = self.getMainImage()

        self.text=self.getText()
        # print(self.text)

        self.formatedtext=self.getFormatedText()
        self.raw=""

        # Look for 10 most common tags in title+text
        self.tags = utils.similarity.findTags(self.title+". "+self.text,self.lang,10)
        # print(self.tags)

        self.rate=0
        self.similarity=0
        self.similarity_with=""

        self.liked=0

        #print("+-[Article] {} ".format(self.lang))
        # self.show()
        Article.nbarticles += 1
        # print("+---[Proceed] in {} s".format(int(time.time()-startime)))

    def getMainImage(self) :
        out_img=""
        if self.service.find('image') is not None :
            type = self.service.find('image').get('type')
            name = self.service.find('image').get('name')
            value = self.service.find('image').text
            section = self.service.find('image').get('section')
            attribute = self.service.find('image').get('attribute')
        else :
            return out_img

        if (name == "class") :
            img_sec=self.soup.find(type, class_=value)
            #print(img_sec)
            if img_sec is not None and self.service.find('image').get('subtype') is not None :
                subtype = self.service.find('image').get('subtype')
                img_sec = img_sec.find(subtype)
                # print(img_sec)

            if img_sec is not None and img_sec.find(section) is not None :
                out_img=img_sec.find(section).get(attribute)

        # relative links
        if out_img is not None and out_img.startswith('/') :
            parsed_web_page = urlparse(self.url)
            dom =  '{uri.scheme}://{uri.netloc}/'.format(uri=parsed_web_page)
            out_img = dom+out_img

        return out_img

    def getText(self) :
        out_text=""
        if self.service.find('text') is not None :
            type = self.service.find('text').get('type')
            name = self.service.find('text').get('name')
            value = self.service.find('text').text
            section = self.service.find('text').get('section')
        else :
            return out_text

        if (name == "class") :
            text_sec=self.soup.find(type, class_=value)
            # print(text_sec)
            if text_sec is not None :
                for t in text_sec.find_all(section):
                    out_text=out_text+utils.utils.sanitizeText(t.get_text())
        return out_text

    def getFormatedText(self) :
        out_text=""
        if self.service.find('text') is not None :
            type = self.service.find('text').get('type')
            name = self.service.find('text').get('name')
            value = self.service.find('text').text
            section = self.service.find('text').get('section')

        if (name == "class") :
            text_sec=self.soup.find(type, class_=value)

        if text_sec is not None :
            for t in text_sec.find_all(section):
                sText=utils.utils.sanitizeText(t.get_text())
                if sText :
                    out_text=out_text+"<p>"+sText+"</p>"
        return out_text

    def printJson(self) :
        return {
            'title': self.title,
            'service': self.service_name,
            'source': self.url,
            'shorturl': self.shorturl,
            'date' : self.date,
            'lang' : self.lang,
            'image': self.image,
            'tags' : self.tags,
            'rate' : self.rate,
            'similarity' : self.similarity,
            'similarity_with' : self.similarity_with,
            'text' : self.text,
            'text_size' : str(len(self.text.split())),
            'liked' : self.liked
        }

    def getTweet(self) :
        tweet_size = 140
        tweet_link_size = 24

        text=self.title
        # print("[Tweet] Text : [{}]".format(text))
        # Add '#' in front of the 3 main tags if in title
        max=3
        nb=0
        if self.tags :
            for w in self.tags :
                if nb >= max : break
                # print("[Tweet] Look for {} in [{}]".format(w,text))
                # Verify if we can add a #
                if w in text.lower() :
                    # print("[Tweet] Found {}".format(w))

                    for v in re.split(' |; |, |\'',text) :
                        # print("[Tweet] Try to Replace {} using {}".format(v,v.lower()))
                        if w == v.lower() and len(text)+tweet_link_size+1 <= tweet_size :
                            text = re.sub(v,'#'+w,text)
                            # First matched tag is enough
                            nb=max
                nb += 1
        # print("[Tweet] Add Tags : [{}]".format(text))

        # Add source if possible
        if len(text)+len(self.service_mention)+2+tweet_link_size <= tweet_size and self.service_mention not in text :
            text += " "+self.service_mention
        # print("[Tweet] Add source : [{}]".format(text))

        # Add url
        # Add main tag after url if not in title
        if len(self.tags) >= 1 :
            maintag = self.tags[0]
            if " " not in maintag and maintag not in text and len(text)+len(maintag)+2+tweet_link_size <= tweet_size :
                text += " "+self.shorturl+" #"+maintag
            else :
                text += " "+self.shorturl
        else :
            text += " "+self.shorturl

        print("+---[Tweet] {}".format(text))
        return text

    def show(self) :
        print("+--[Article] {} ".format(self.title))
        tags = ','.join(self.tags)

        # Length and time to read
        length = len(self.text.split())
        if length < 300 :
            tpslect = "< 1"
        else :
            t = int(length/300)
            tpslect = str(t)
        print("+---[content] {} words ({} min)".format(str(length),tpslect))

        print("+---[url] {} ".format(self.url))
        if self.image : print("+---[img] {} ".format(self.image))

        print("+---[tags] [{}]".format(tags))
