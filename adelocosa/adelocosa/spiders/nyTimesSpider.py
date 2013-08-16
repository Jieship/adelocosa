import time

from scrapy.spider import BaseSpider
from scrapy.selector import HtmlXPathSelector
from scrapy.http import Request
from adelocosa.items import AdelocosaItem

class NYTimesSpider(BaseSpider):
    name = "NYTimes"
    allowed_domains = ["nytimes.com"]
    
    start_urls = ["http://query.nytimes.com/search/advanced/?srchst=nyt#/*/from20100101to20131231/document_type%3A%22article%22/1/allauthors/oldest/"]
    # selects for all days between 2010-01-01 and 2013-12-31

    def page_type(url):
        if("search/advanced" in url):
            return "directory"
        else:
            return "article"

    def parse(self, response):
        if(response.status == 404):
            # do nothing
            return []
        elif("search/advanced" in response.url):
            # page is a directory of articles
            hxs = HtmlXPathSelector(response)
            articleLinks = hxs.select('//div[@class="entry"]//h3/a/@href').extract()
            return [Request(url=link, callback=self.parse) for link in articleLinks]
        else:
            # page is an article
            item = HuffpostItem()
            hxs = HtmlXPathSelector(response)
            colXSList = hxs.select('//div[@class="col entry_right full"]')
            colXS = None
            if(len(colXSList) > 0):
                colXS = colXSList[0]
            else:
                return []
            
            item['source'] = self.allowed_domains[0]
            item['url'] = response.url
            item['date'] = response.url[30:40]  #pretty hacky, I know
            item['headline'] = colXS.select('h1/text()')[0].extract().strip()

            imgXSList = colXS.select('//img[@class="pinit"]')
            if(len(imgXSList) < 1):
                #found no images, discard article
                return []
            else:
                imgXS = imgXSList[0]
                urlList = imgXS.select('@src').extract()
                item['imgURL'] = urlList[0] if len(urlList) > 0 else None
                widthList = imgXS.select('@width').extract()
                item['imgWidth'] = widthList[0] if len(widthList) > 0 else None
                heightList = imgXS.select('@height').extract()
                item['imgHeight'] = heightList[0] if len(heightList) > 0 else None

                return [item]

        #filename = response.url.split('/')[-2]
        #open(filename, "wb").write(response.body)

