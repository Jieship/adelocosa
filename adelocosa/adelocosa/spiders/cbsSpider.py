from scrapy.spider import BaseSpider
from scrapy.selector import HtmlXPathSelector
from scrapy.http import Request
from adelocosa.items import AdelocosaItem

class CbsSpider(BaseSpider):
    name = "CBS"
    allowed_domains = ["cbsnews.com"]
    
    start_urls = ["http://www.cbsnews.com/2003-250_162-0.html"]
    # selects for all days between 2010-01-01 and 2013-12-31
    start_urls += [("http://www.cbsnews.com/2003-250_162-0-%d.html" % i) \
            for i in range(1,1524)]

    def parse_article(self, response):
        item = AdelocosaItem()
        hxs = HtmlXPathSelector(response)
        colXSList = hxs.select('//div[@class="col entry_right full"]')
        colXS = None
        if(len(colXSList) > 0):
            colXS = colXSList[0]
        else:
            return
        
        item['source'] = self.allowed_domains[0]
        item['url'] = response.url
        item['date'] = response.url[30:40]  #pretty hacky, I know
        item['headline'] = colXS.select('h1/text()')[0].extract().strip()

        imgXSList = colXS.select('//img[@class="pinit"]')
        if(len(imgXSList) < 1):
            #found no images, discard article
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

            return item

    def parse(self, response):
        if(response.status == 404):
            # do nothing
            return
        elif("2003-250_162-0" in response.url):
            # page is a directory of articles
            hxs = HtmlXPathSelector(response)
            articleLinks = hxs.select('//div[@class="entry"]//h3/a/@href').extract()
            return [Request(url=link, callback=self.parse) for link in articleLinks]
        else:
            # page is an article
            return self.parse_article(response)
            
        #filename = response.url.split('/')[-2]
        #open(filename, "wb").write(response.body)

