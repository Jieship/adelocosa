from scrapy.spider import BaseSpider
from scrapy.selector import HtmlXPathSelector
from scrapy.http import Request
from adelocosa.items import AdelocosaItem

class politicoSpider(BaseSpider):
    name = "Politico"
    allowed_domains = ["politico.com"]
    logFile = open(name + ".log", "w")
    
    start_urls = []
    # selects for all days between 2010-01-01 and 2013-12-31
    # I needed a query to get any results, so I used "have", a common word
    start_urls += [("http://find.politico.com/index.cfm?adv=0&key=have&dt=all&reporters=&sort=date&currentPage=%d" % i) for i in range(1,3700)] #3667

    def parse_article(self, response):
        item = AdelocosaItem()
        hxs = HtmlXPathSelector(response)
        colXSList = hxs.select('//div[contains(@class,"article") or contains(@class,"post")]')
        colXS = None
        if(len(colXSList) > 0):
            colXS = colXSList[0]
        else:
            self.logFile.write("colXS missing:\t" + response.url + "\n")
            returxpathn
        
        item['source'] = self.allowed_domains[0]
        item['url'] = response.url
        item['headline'] = colXS.select('h1/text()')[0].extract()
        
        blXS = colXS.select('div[contains(@class,"byline")]')
        dateXSL = blXS.select('h5/abbr/text()')
        if len(dateXSL) > 0:
            item['date'] = dateXSL[0].extract().strip().split(' ')[0]
        else:
            blStr = blXS[0].extract()
            item['date'] = blStr[blStr.find('|')+1:].strip().split(' ')[0]  
                #pretty hacky, I know
        

        imgXSList = colXS.select('//img[contains(@class,"border")]')
        if(len(imgXSList) < 1):
            #found no images, discard article
            self.logFile.write("image missing:\t" + response.url + "\n")
            return
        else:
            imgXS = imgXSList[0]
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
        elif("find.politico.com/" in response.url):
            # page is a directory of articles
            hxs = HtmlXPathSelector(response)
            articleLinks = hxs.select('//ul[contains(@class,"main-stories-list")]/li/h3/a/@href').extract()
            return [Request(url=link, callback=self.parse) for link in articleLinks]
        else:
            # page is an article
            return self.parse_article(response)
