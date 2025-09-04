import scrapy

class LocalchItem(scrapy.Item):
    firma_adi = scrapy.Field()
    adres = scrapy.Field()
    telefon = scrapy.Field()
    email = scrapy.Field()
    website = scrapy.Field()
    url = scrapy.Field()
