import time
import pytz
from datetime import datetime

import utils

current_milli_time = lambda: int(round(time.time() * 1000))

class Article:
    nbarticles = 0

    def __init__(self, service, title, url, lang):
        startime = time.time()

        self.id = str(current_milli_time())
        self.service = service
        self.title = title
        self.url = url
        self.lang = lang
        self.date = datetime.now(pytz.timezone('Europe/Paris')).isoformat(),

        self.soup = utils.services.getArticleContent(self.url)
        # print(self.soup)

        self.image = self.getMainImage()

        self.text=self.getText()
        # print(self.text)

        self.formatedtext=self.getFormatedText()
        self.raw=""

        # Look for tags in title+text
        self.tags = utils.similarity.findTags(self.title+". "+self.text,self.lang)
        # print(self.tags)

        self.rate=0
        self.similarity=0
        self.similarity_with=""

        self.liked=0

        #print("+-[Article] {} ".format(self.lang))
        self.show()
        Article.nbarticles += 1
        print("+---[Proceed] in {}  s".format(int(time.time()-startime)))

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
        if img_sec is not None and img_sec.find(section) is not None :
            out_img=img_sec.find(section).get(attribute)
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

    #depreciated
    # def getTags(self) :
    #     out_tags=[]
    #     if self.service.find('text') is not None :
    #         type = self.service.find('text').get('type')
    #         name = self.service.find('text').get('name')
    #         value = self.service.find('text').text
    #         section = self.service.find('text').get('section')
    #
    #     if (name == "class") :
    #         tags_sec=self.soup.find(type, class_=value)
    #     if tags_sec is not None and tags_sec.find_all(section) is not None :
    #         for t in tags_sec.find_all(section):
    #             tag = t.get_text().lower()
    #             tag = tag.replace("-","")
    #             tag = tag.replace(" ","")
    #             tag = tag.replace("...","")
    #             print(tag)
    #             if tag : out_tags.append(tag)
    #     return out_tags

    def printJson(self) :
        return {
            'title': self.title,
            'service': self.service.find('id').text,
            'source': self.url,
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

    def getTitleWithTags(self) :
        title = self.title
        for w in title.split(" ") :
            for x in self.tags :
                if x == w.lower() :
                    title = title.replace(w,"#"+x)

        return title

    def show(self) :
        print("+--[Article] {} ".format(self.title))
        print("+---[url] {} ".format(self.url))
        if self.image : print("+---[img] {} ".format(self.image))
        print("+---[content] {} words ".format(str(len(self.text.split()))))
        print("+---[tags] {} ".format(self.tags))
        # print("+---[content] {} words in {} ".format(str(len(self.text.split()),self.lang)))

        #print("+--[from] {} in {} ".format(self.service, self.lang))
