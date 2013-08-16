from scrapy.spider import BaseSpider
from scrapy.selector import HtmlXPathSelector
from scrapy.http import Request
from adelocosa.items import AdelocosaItem

class HuffPostSpider(BaseSpider):
    name = "HuffingtonPost"
    allowed_domains = ["huffingtonpost.com"]
    logFile = open(name + ".log", "w")
    
    start_urls = []
    # selects for all days between 2010-01-01 and 2013-12-31
    for year in range(2010, 2014):
        for month in range(1, 13):
            for day in range(1, 32):
                curUrl = "http://www.huffingtonpost.com/politics/the-news/"
                curUrl += ("%04d" % year) + "/"
                curUrl += ("%02d" % month) + "/" + ("%02d" % day) + "/"
                start_urls.append(curUrl)

    def getImgXS(self, colXS):
        XSList = colXS.select('//img[contains(@class,"pinit")]')
        if(len(XSList) > 0):
            return XSList[0]
        
        XSList = colXS.select('div[contains(@class,"margin_bottom_10")]/img')
        if(len(XSList) > 0):
            return XSList[0]

        XSList = colXS.select('//div[contains(@class,"big_photo")]/img')
        if(len(XSList) > 0):
            return XSList[0]

        return None


    def parse_article(self, response):
        item = AdelocosaItem()
        hxs = HtmlXPathSelector(response)
        colXSList = hxs.select('//div[contains(@class,"col entry_right full")]')
        colXS = None
        if(len(colXSList) > 0):
            colXS = colXSList[0]
        else:
            self.logFile.write("colXS missing:\t" + response.url + "\n")
            return
        
        item['source'] = self.allowed_domains[0]
        item['url'] = response.url
        item['date'] = response.url[30:40]  # pretty hacky, I know
        item['headline'] = colXS.select('h1/text()')[0].extract().strip()

        imgXS = self.getImgXS(colXS)
        if(imgXS == None):
            #found no images, discard article
            self.logFile.write("image missing:\t" + response.url + "\n")
            return
        else:
            urlList = imgXS.select('@src').extract()
            if len(urlList) > 0:
                item['imgUrl'] = urlList[0]
            widthList = imgXS.select('@width').extract()
            if len(widthList) > 0:
                item['imgWidth'] = widthList[0]
            heightList = imgXS.select('@height').extract()
            if len(heightList) > 0:
                item['imgHeight'] = heightList[0]

            self.logFile.write("SUCCESS:\t\t" + response.url + "\n")
            return item

    def parse(self, response):
        if(response.status == 404):
            # do nothing
            return
        elif("huffingtonpost.com/politics/the-news" in response.url):
            # page is a directory of articles
            hxs = HtmlXPathSelector(response)
            articleLinks = hxs.select('//div[contains(@class,"entry")]//h3/a/@href').extract()
            return [Request(url=link, callback=self.parse) for link in articleLinks]
        else:
            # page is an article
            return self.parse_article(response)
