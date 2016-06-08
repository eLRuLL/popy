from scrapy import Spider, Request
from scrapy.http import Response
from urllib import urlencode
from copy import deepcopy


class MesasCollectorSpider(Spider):
    name = 'mesas'

    request_url = 'https://resultadoselecciones2016.onpe.gob.pe/PRP2V2016/ajax.php'

    ambitos = {
        'P': 'Peru',
        'E': 'Extrajero',
    }

    custom_settings = {
        'DEFAULT_REQUEST_HEADERS': {
            'X-Requested-With': 'XMLHttpRequest',
            'Content-Type': 'application/x-www-form-urlencoded',
        }
    }

    def parse_error(self, response):
        if not isinstance(response, Response):
            response = response.request
        item = response.meta.get('item', {})
        item['error'] = response.url
        item['request_body'] = response.body
        return item

    def start_requests(self):
        for ambito_code, ambito_name in self.ambitos.items():
            body = {
                '_clase': 'ubigeo',
                '_accion': 'getDepartamentos',
                'dep_id': '',
                'tipoElec': '',
                'tipoC': 'acta',
                'modElec': '',
                'ambito': ambito_code,
                'pantalla': '',
            }
            yield Request(
                url=self.request_url,
                body=urlencode(body),
                callback=self.parse_departament,
                errback=self.parse_error,
                method='post',
                meta={
                    'item': {'ambito': ambito_name},
                }
            )

    def parse_departament(self, response):
        self.logger.info('parse_department')
        for code in response.xpath('//option[not(@selected)]'):
            item = deepcopy(response.meta['item'])
            item.update(
                department_code=code.xpath('./@value').extract_first(),
                department_name=code.xpath('./text()').extract_first(),
            )
            body = {
                '_clase': 'ubigeo',
                '_accion': 'getProvincias',
                'tipoC': 'acta',
                'tipoElec': '',
                'modElec': '',
                'dep_id': code.xpath('./@value').extract_first(),
            }
            yield Request(
                url=self.request_url,
                body=urlencode(body),
                callback=self.parse_province,
                errback=self.parse_error,
                method='post',
                meta={'item': item},
            )

    def parse_province(self, response):
        self.logger.info('parse_province')
        for code in response.xpath('//option[not(@selected)]'):
            item = deepcopy(response.meta['item'])
            item.update(
                province_code=code.xpath('./@value').extract_first(),
                province_name=code.xpath('./text()').extract_first(),
            )
            body = {
                '_clase': 'ubigeo',
                '_accion': 'getDistritos',
                'tipoC': 'acta',
                'prov_id': code.xpath('./@value').extract_first(),
                'tipoElec': '',
                'modElec': '',
            }
            yield Request(
                url=self.request_url,
                body=urlencode(body),
                callback=self.parse_district,
                errback=self.parse_error,
                method='post',
                meta={'item': item},
            )

    def parse_district(self, response):
        self.logger.info('parse_district')
        for code in response.xpath('//option[not(@selected)]'):
            item = deepcopy(response.meta['item'])
            item.update(
                district_code=code.xpath('./@value').extract_first(),
                district_name=code.xpath('./text()').extract_first(),
            )
            body = {
                '_clase': 'actas',
                '_accion': 'getLocalesVotacion',
                'tipoElec': '',
                'ubigeo': code.xpath('./@value').extract_first(),
            }
            yield Request(
                url=self.request_url,
                body=urlencode(body),
                callback=self.parse_local,
                errback=self.parse_error,
                method='post',
                meta={'item': item},
            )

    def parse_local(self, response):
        self.logger.info('parse_local')
        for code in response.xpath('//option[not(@selected)]'):
            actas_por, ubigeo = code.xpath('./@value').extract_first().split('?')
            item = deepcopy(response.meta['item'])
            item.update(
                local_code=actas_por,
                local_name=code.xpath('./text()').extract_first(),
            )
            body = {
                '_clase': 'actas',
                '_accion': 'displayActas',
                'tipoElec': '10',
                'ubigeo': ubigeo,
                'actasPor': actas_por,
                'ubigeoLocal': ubigeo,
                'page': 'undefined',
            }
            yield Request(
                url=self.request_url,
                body=urlencode(body),
                callback=self.parse_mesas,
                errback=self.parse_error,
                method='post',
                meta={'item': item},
            )

    def parse_mesas(self, response):
        self.logger.info('parse_mesas')
        for mesa in response.xpath('(//table)[1]//td//a/text()').extract():
            item = deepcopy(response.meta['item'])
            item['mesa'] = mesa
            yield item
