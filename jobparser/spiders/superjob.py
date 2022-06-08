import scrapy
from scrapy.http import HtmlResponse
from jobparser.items import JobparserItem


class SuperjobSpider(scrapy.Spider):
    name = 'superjob'
    allowed_domains = ['superjob.ru']
    start_urls = ['https://www.superjob.ru/vacancy/search/?'
                  'keywords=python&geo%5Bt%5D%5B0%5D=4&geo%5Bt%5D%5B1%5D=14']

    def parse(self, response: HtmlResponse):
        main_url = 'https://www.superjob.ru'
        next_page = response.xpath("//a[contains(@class, 'f-test-link-Dalshe')]/@href").get()
        if next_page:
            yield response.follow(next_page, callback=self.parse)
        links = response.xpath("//a[contains(@href, 'vakansii') and contains(@href, 'html')]/@href").getall()
        for link in links:
            yield response.follow(main_url + link, callback=self.parse_vacancy)

    def parse_vacancy(self, response: HtmlResponse):
        print()
        name = response.xpath('//h1//text()').get()
        salary = response.xpath("//span[@class='_2eYAG _3y3l6 z4PWH t0SHb']/text()").getall()
        url = response.url
        yield JobparserItem(name=name, salary=salary, url=url)
