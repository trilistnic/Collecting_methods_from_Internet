# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
from pymongo import MongoClient


class JobparserPipeline:
    def __init__(self):
        client = MongoClient('localhost', 27017)
        self.mongodb = client.vacancies

    def process_item(self, item, spider):
        if spider.name == 'hh':
            item['salary_min'], item['salary_max'], item['currency'] = self.salary_hh(item['salary'])
        else:
            item['salary_min'], item['salary_max'], item['currency'] = self.salary_superjob(item['salary'])

        del item['salary']
        collection = self.mongodb[spider.name]
        collection.insert_one(item)
        return item

    def salary_hh(self, data):
        for i in range(len(data)):
            data[i] = data[i].replace('\xa0', '')
        if data[0] == 'до ' and len(data) == 4:
            salary_min = None
            salary_max = int(data[1])
            salary_currency = data[3]
        elif data[0] == 'от ' and len(data) == 4:
            salary_min = int(data[1])
            salary_max = None
            salary_currency = data[3]
        elif len(data) == 6:
            salary_min = int(data[1])
            salary_max = int(data[3])
            salary_currency = data[5]
        else:
            salary_min = None
            salary_max = None
            salary_currency = None
        return salary_min, salary_max, salary_currency

    def salary_superjob(self, data):
        for i in range(len(data)):
            data[i] = data[i].replace('\xa0', '')
        if data[0] == 'до' and len(data) == 3:
            salary_min = None
            salary_max = int(''.join(x for x in data[2] if x.isdigit()))
            salary_currency = ''.join(x for x in data[2] if x.isalpha())
        elif data[0] == 'от' and len(data) == 3:
            salary_min = int(''.join(x for x in data[2] if x.isdigit()))
            salary_max = None
            salary_currency = ''.join(x for x in data[2] if x.isalpha())
        elif len(data) == 4:
            salary_min = int(data[0])
            salary_max = int(data[1])
            salary_currency = data[3]
        else:
            salary_min = None
            salary_max = None
            salary_currency = None
        return salary_min, salary_max, salary_currency
