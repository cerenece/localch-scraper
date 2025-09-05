import scrapy

class LocalchItem(scrapy.Item):
    Firma_Adi = scrapy.Field()
    Adres = scrapy.Field()
    Telefon = scrapy.Field()
    Email = scrapy.Field()
    Website = scrapy.Field()
    URL = scrapy.Field()
