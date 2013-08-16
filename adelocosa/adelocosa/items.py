# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

from scrapy.item import Item, Field

class AdelocosaItem(Item):
    # define the fields for your item here like:
    # name = Field()

    source = Field()
    url = Field()
    date = Field()
    headline = Field()
    imgUrl = Field()
    imgWidth = Field()
    imgHeight = Field()
    articleLen = Field()
    location = Field()
    pass
