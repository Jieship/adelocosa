from scrapy.spider import BaseSpider
from scrapy.selector import HtmlXPathSelector
from scrapy.http import Request
from adelocosa.items import AdelocosaItem

class ReutersSpider(BaseSpider):
    name = "Reuters"
    allowed_domains = ["reuters.com"]
    logFile = open("Reuters.log", "w")
    
    start_urls = []
    # selects for all days between 2010-01-01 and 2013-12-31
    for year in range(2010, 2014):
        for month in range(1, 13):
            for day in range(1, 32):
                curUrl = "http://www.reuters.com/news/archive/domesticNews?date="
                curUrl += ("%02d" % month) + ("%02d" % day) + ("%04d" % year)
                start_urls.append(curUrl)

    def parse_article(self, response):
        item = AdelocosaItem()
        hxs = HtmlXPathSelector(response)
        colXSList = hxs.select('//div[contains(@class,"column2 gridPanel")]')
        colXS = None
        if(len(colXSList) > 0):
            colXS = colXSList[0]
        else:
            self.logFile.write("colXS missing:\t" + response.url + "\n")
            return
        
        item['source'] = self.allowed_domains[0]
        item['url'] = response.url
        item['date'] = response.url[31:41]  #pretty hacky, I know
        item['headline'] = colXS.select('h1/text()')[0].extract()

        imgXSList = colXS.select('div[contains(@class,"relatedPhoto")]/img') 
        if(len(imgXSList) < 1):
            #found no images, discard article
            self.logFile.write("image missing:\t" + response.url + "\n")
            return
        else:
            imgXS = imgXSList[0]
            item['imgHtml'] = imgXS.extract()
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
        elif("news/archive/domesticNews" in response.url):
            # page is a directory of articles
            hxs = HtmlXPathSelector(response)
            articlefStr = '//div[@id="moreSectionNews"]'
            articlefStr += '/div/div/div[contains(@class,"feature")]/h2/a/@href'
            articleLinks = hxs.select(articlefStr).extract()
            return [Request(url="http://" + self.allowed_domains[0] + link, \
                            callback=self.parse) for link in articleLinks]
        else:
            # page is an article
            return self.parse_article(response)
