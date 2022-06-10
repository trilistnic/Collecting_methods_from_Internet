import scrapy
from scrapy.http import HtmlResponse
from productparser.items import ProductparserItem
from scrapy.loader import ItemLoader


class CastoramaSpider(scrapy.Spider):
    name = 'castorama'
    allowed_domains = ['castorama.ru']

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.start_urls = [f"https://www.castorama.ru/catalogsearch/result/?q={kwargs.get('query')}"]

    def parse(self, response: HtmlResponse):
        next_page = response.xpath("//a[@class = 'next i-next']/@href").get()
        if next_page:
            yield response.follow(next_page, callback=self.parse)
        links = response.xpath("//a[@class ='product-card__img-link']")
        for link in links:
            yield response.follow(link, callback=self.parse_data)

    def parse_data(self, response: HtmlResponse):
        loader = ItemLoader(item=ProductparserItem(), response=response)
        loader.add_xpath('name', '//h1/text()')
        loader.add_xpath('price', "//span[@class = 'price']//text()")
        loader.add_xpath('photos', "//img[@class = 'top-slide__img swiper-lazy swiper-lazy-loaded']/@src | "
                                   "//img[@class = 'top-slide__img swiper-lazy']/@data-src")
        loader.add_value('url', response.url)
        yield loader.load_item()
