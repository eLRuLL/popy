from scrapy import Spider


class MesasCollectorSpider(Spider):
    name = 'mesas'

    start_urls = [
        'https://resultadoselecciones2016.onpe.gob.pe/PRP2V2016/Actas-por-Ubigeo.html',
    ]

    request_url = 'https://resultadoselecciones2016.onpe.gob.pe/PRP2V2016/ajax.php'

    def parse(self, response):
        pass
