from lxml import html
import requests
from pymongo import MongoClient

headers = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                         'AppleWebKit/537.36 (KHTML, like Gecko) '
                         'Chrome/101.0.0.0 Safari/537.36'}
client = MongoClient('127.0.0.1', 27017)
db = client['news']
all_news = db.all_news


def dom(url_link):
    response = requests.get(url_link, headers=headers)
    xpath_dom = html.fromstring(response.text)
    return xpath_dom


def mail(url_link):
    links = dom(url_link).xpath("//a[contains(@class,'photo_full') and not (@data-gallery-url) "
                                "or contains(@class,'list__text')]/@href")
    for link in links:
        item_info = {}
        new_dom = dom(link)
        item_info['source'] = new_dom.xpath("//span[contains(@class,'note')]/a/span/text()")
        item_info['name'] = new_dom.xpath("//h1/text()")
        item_info['link'] = link
        item_info['date'] = ''.join(new_dom.xpath("//span/@datetime")).split('T')[0]

        all_news.insert_one(item_info)


def yandex(url_link):
    links = dom(url_link).xpath("//div[contains(@class, 'mg-grid__item')]")
    for link in links:
        item_info = {}
        if link.xpath(".//h2/a/@href"):
            item_info['source'] = link.xpath(".//a[contains(@class, 'mg-card__source-link')]/text()")
            item_info['name'] = ''.join(link.xpath(".//h2/a/text()")).replace('\xa0', ' ')
            item_info['link'] = link.xpath(".//h2/a/@href")
            item_info['date'] = link.xpath(".//span[contains(@class, 'mg-card-source__time')]/text()")

            all_news.insert_one(item_info)


def lenta(url_link):
    links = dom(url_link).xpath("//a[contains(@class, '_topnews')]")
    for link in links:
        item_info = {}
        item_info['source'] = url_link
        item_info['name'] = link.xpath(".//*[contains(@class, 'title') and not (contains(@class, 'titles'))]/text()")
        item_info['link'] = url_link+link.xpath("./@href")[0]
        item_info['date'] = link.xpath(".//time/text()")

        all_news.insert_one(item_info)


mail('https://news.mail.ru/')
yandex('https://yandex.ru/news/')
lenta('https://lenta.ru/')
