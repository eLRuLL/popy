import json
# from urllib import urlretrieve

import requests
from w3lib.html import remove_tags
import scrapy
from scrapy.http import FormRequest, Request

from onpe_crawler.items import OnpeCrawlerItem


def read_from_file():
    mesas_url = "https://www.dropbox.com/s/67p9z03r9i6bj0v/mesas.jl?dl=1"
    res = requests.get(mesas_url)
    if res.status_code != 200:
        raise IOError("Mesas file in Dropbox cannot be read")
    return [json.loads(i) for i in res.content.splitlines()]


class QuakerSpider(scrapy.Spider):
    name = "quaker"
    allowed_domains = ["onpe.gob.pe"]
    base_url = 'https://resultadoselecciones2016.onpe.gob.pe/PRP2V2016/ajax.php'
    start_url = 'https://resultadoselecciones2016.onpe.gob.pe/PRP2V2016/'
    all_ubigeos = read_from_file()

    def start_requests(self):
        yield Request(url=self.start_url,
                      headers={'X-Requested-With': 'XMLHttpRequest'},
                      callback=self.get_mesas)

    def get_mesas(self, response):
        for i in self.all_ubigeos:
            ubigeo = i['mesa']
            local_code = i['local_code']
            yield FormRequest(url=self.base_url,
                           headers={'X-Requested-With': 'XMLHttpRequest'},
                           formdata={
                               '_clase': 'actas',
                               '_accion': 'displayActas',
                               'tipoElec': '10',
                               'ubigeo': ubigeo,
                               'actasPor': local_code,
                               'ubigeoLocal': ubigeo,
                               'page': 'undefined',
                           },
                           meta={'ubigeo': ubigeo,
                                 'department': i['department_name'],
                                 'province': i['province_name'],
                                 'district': i['district_name']},
                           callback=self.parse)

    def parse(self, response):
        ubigeo = response.meta['ubigeo']

        filename = "ubigeo_" + ubigeo + '.html'
        with open(filename, 'wb') as f:
            f.write(response.body)

        tables = response.xpath('//td/a/text()').extract()
        for table in tables:
            meta = response.meta
            meta['mesa'] = table
            yield FormRequest(url=self.base_url,
                            headers={'X-Requested-With': 'XMLHttpRequest'},
                            formdata={
                                '_clase': 'mesas',
                                '_accion':'displayMesas',
                                'ubigeo': ubigeo,
                                'nroMesa': table,
                                'tipoElec': '10',
                                'page': '1',
                                'pornumero': '1',
                            },
                            meta=meta,
                            callback=self.parse_mesa)

    def parse_mesa(self, response):
        filename = "mesa_" + response.meta['mesa'] + '.html'
        with open(filename, 'wb') as f:
            f.write(response.body)

        meta = response.meta
        item = OnpeCrawlerItem()
        ubigeo = response.xpath("//table[@class='table14']//tr[2]//td").extract()
        ubigeo = [remove_tags(i) for i in ubigeo]
        item['content_results'] = response.xpath("//div[@class='contenido-resultados']").extract_first()
        item['department'] = meta['department']
        item['province'] = meta['province']
        item['district'] = meta['district']
        item['local'] = ubigeo[3]
        item['address'] = ubigeo[4]

        mesa_info = response.xpath("//table[@class='table15']//tr[2]//td/text()").extract()
        item['electors'] = mesa_info[0]
        item['voters'] = mesa_info[1]
        item['acta_status'] = mesa_info[2].strip()
        item['resolutions'] = response.xpath('//div[contains(@class, "pbot30_acta")]/text()[3]').extract_first().strip()
        item['resolutions_note'] = response.xpath('//div[contains(@class, "pbot30_acta")]/p[2]/text()').extract_first()

        votes = response.xpath('//div[@class="cont-tabla1"]//td/text()').extract()
        item['votes_ppk'] = votes[3].strip()
        item['votes_fp'] = votes[5].strip()
        item['votes_blank'] = votes[7].strip()
        item['votes_null'] = votes[9].strip()
        item['votes_contested'] = votes[11].strip()
        item['votes_total'] = votes[13].strip()

        item['table_number'] = response.xpath("//table[@class='table13']//td/text()").extract_first()
        item['copy_number'] = response.xpath('//table[@class="table13"]//td/text()').extract()[1].strip()
        href = response.xpath('//a/@href').extract_first()
        item['acta_image_url'] = "{}/{}".format(self.start_url, href)
        # filename = "acta_mesa_" + item['table_number'] + '.pdf'
        # urlretrieve(item['acta_image_url'], filename)
        return item
