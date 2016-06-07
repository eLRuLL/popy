import scrapy
from scrapy.http import FormRequest, Request


class QuakerSpider(scrapy.Spider):
    name = "quaker"
    allowed_domains = ["onpe.gob.pe"]
    base_url = 'https://resultadoselecciones2016.onpe.gob.pe/PRP2V2016/ajax.php'
    start_url = 'https://resultadoselecciones2016.onpe.gob.pe/PRP2V2016/'

    def start_requests(self):
        yield Request(url=self.start_url,
                      headers={'X-Requested-With': 'XMLHttpRequest'},
                      callback=self.get_mesas)

    def get_mesas(self, response):
        ubigeo = '150301'
        return [FormRequest(url=self.base_url,
                           headers={'X-Requested-With': 'XMLHttpRequest'},
                           formdata={
                               '_clase': 'actas',
                               '_accion': 'displayActas',
                               'tipoElec': '10',
                               'ubigeo': ubigeo,
                               'actasPor': '3907',
                               'ubigeoLocal': ubigeo,
                               'page': 'undefined',
                           },
                           meta={'ubigeo': ubigeo},
                           callback=self.parse)]

    def parse(self, response):
        ubigeo = response.meta['ubigeo']

        filename = "ubigeo_" + ubigeo + '.html'
        with open(filename, 'wb') as f:
            f.write(response.body)

        # mesas
        tables = response.xpath('//td/a/text()').extract()
        for table in tables:
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
                            meta={'mesa': table},
                            callback=self.parse_mesa)

    def parse_mesa(self, response):
        filename = "mesa_" + response.meta['mesa'] + '.html'
        with open(filename, 'wb') as f:
            f.write(response.body)
