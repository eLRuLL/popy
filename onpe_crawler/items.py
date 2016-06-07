# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class OnpeCrawlerItem(scrapy.Item):
    country = scrapy.Field()
    department = scrapy.Field()
    province = scrapy.Field()
    district = scrapy.Field()
    local = scrapy.Field()
    address = scrapy.Field()
    table_number = scrapy.Field()
    copy_number = scrapy.Field()
    with_image = scrapy.Field()  # boolean
    processed = scrapy.Field()  # boolean
    electors = scrapy.Field()
    voters = scrapy.Field()
    acta_status = scrapy.Field()
    acta_image = scrapy.Field()
    resolutions = scrapy.Field()  # Lista de resoluciones
    resolutions_note = scrapy.Field()  # : El valor consignado en el acta presenta ilegibilidad
    votes_ppk = scrapy.Field()
    votes_fp = scrapy.Field()
    votes_blank = scrapy.Field()
    votes_null = scrapy.Field()
    votes_contested = scrapy.Field()
    votes_total = scrapy.Field()
