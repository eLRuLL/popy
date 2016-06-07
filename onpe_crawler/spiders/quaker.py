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
                      callback=self.parse)

    # curl -v 'https://resultadoselecciones2016.onpe.gob.pe/PRP2V2016/ajax.php' --data '_claas&_accion=displayMesas&ubigeo=040129&nroMesa=007246&tipoElec=10&page=1&pornumero=1' -H 'User-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10.11; rv:46.0) Gecko/20100101 Firefox/46.0' -H 'X-Requested-With: XMLHttpRequest'
    def parse(self, response):
        ubigeo = "040129"
        mesa = '007246'
        return [FormRequest(url=self.base_url,
                            headers={'X-Requested-With': 'XMLHttpRequest'},
                            formdata={
                                '_clase': 'mesas',
                                '_accion':'displayMesas',
                                'ubigeo': ubigeo,
                                'nroMesa': mesa,
                                'tipoElec': '10',
                                'page': '1',
                                'pornumero': '1',
                            },
                            meta={'mesa': mesa},
                            callback=self.parse_mesa)]

    def parse_mesa(self, response):
        filename = "mesa_" + response.meta['mesa'] + '.html'
        with open(filename, 'wb') as f:
            f.write(response.body)
