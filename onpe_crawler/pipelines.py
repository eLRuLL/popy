# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html


class OnpeCrawlerPipeline(object):
    def process_item(self, item, spider):
        return item


class FieldsPipeline(object):

    fields_to_count = {
        'ambito',
        'department_name',
        'province_name',
        'district_name',
        'local_name',
    }

    def process_item(self, item, spider):
        for field, value in item.items():
            if field == 'ambito':
                spider.crawler.stats.inc_value(value)
            elif field == 'department_name':
                spider.crawler.stats.inc_value('{}/{}'.format(item['ambito'], value))
            elif field == 'province_name':
                spider.crawler.stats.inc_value('{}/{}/{}'.format(item['ambito'], item['department_name'], value))
            elif field == 'district_name':
                spider.crawler.stats.inc_value('{}/{}/{}/{}'.format(item['ambito'], item['department_name'], item['province_name'], value))
            elif field == 'local_name':
                spider.crawler.stats.inc_value('{}/{}/{}/{}/{}'.format(item['ambito'], item['department_name'], item['province_name'], item['district_name'], value))
        return item
