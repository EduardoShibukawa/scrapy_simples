# -*- coding: utf-8 -*-
from scrapy import Spider, Request
from scrapy.loader import ItemLoader
from urlparse import urlparse, parse_qs


from noticias.items import NoticiasItem

import re


class ExameNoticiasSpider(Spider):
    name = 'exame_noticias'
    #allowed_domains = ['http://exame.abril.com.br/negocios']
    #start_urls = ['http://http://exame.abril.com.br/negocios/']

    def start_requests(self):
            yield Request(
                'https://www.google.com.br/search?dcr=0&biw=1366&bih=675&tbs=cdr%3A1%2Ccd_min%3A8%2F1%2F2017%2Ccd_max%3A8%2F31%2F2017%2Csbd%3A1&q=allintitle%3A+petrobras+site%3Ahttp%3A%2F%2Fexame.abril.com.br%2Fnegocios&oq=allintitle%3A+petrobras+site%3Ahttp%3A%2F%2Fexame.abril.com.br%2Fnegocios&gs_l=psy-ab.3...78090.82631.0.83027.4.4.0.0.0.0.92.354.4.4.0....0...1.1.64.psy-ab..0.0.0.WlXDGqCzjvM'
            )
    
    def format_google_url(self, url):                       
        return parse_qs(urlparse(url).query)['q'][0]

    def parse(self, response):
        news = response.xpath('//*[@class="r"]')
        for new in news:                    
            exame_url = new.xpath('.//a/@href').extract_first()
            if '/url?' in exame_url:
                exame_url = self.format_google_url(exame_url)                    
            yield Request(str(exame_url), callback=self.parse_exame)

        next_page = response.xpath('//*[@class="pn"]/@href').extract_first()        
        if next_page:
            yield response.follow(next_page, self.parse)
            
    def parse_exame(self, response):                                        
        titulo = "".join([        
                response.xpath('//*[@class="article-title"]/text()').extract_first(),
                '\n' ,
                response.xpath("//*[@class='article-subtitle']/text()").extract_first()
        ])

        data_sem_formato = response.xpath('//*[@class="article-date"]/span/text()').extract_first()                    
        data_atualizacao = re.search('\d{2} \w{3} \d{4}', data_sem_formato).group(0)        

        conteudo = response.xpath('//*[@class="article-content"]/p/text()').extract()

        l = ItemLoader(item=NoticiasItem(), response=response)
        l.add_value('titulo', titulo)
        l.add_value('data_atualizacao', data_atualizacao)
        l.add_value('conteudo', conteudo)

        yield l.load_item()                                