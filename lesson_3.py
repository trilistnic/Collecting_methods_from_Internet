from pymongo import MongoClient
from bs4 import BeautifulSoup as bs
import requests
from pprint import pprint
import re

search_vacancy = input(f'Введите должность для поиска:')
main_url = 'https://hh.ru/'
url = 'search/vacancy'
params = {'text': {search_vacancy}, 'items_on_page': '20'}
headers = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                         'AppleWebKit/537.36 (KHTML, like Gecko) '
                         'Chrome/101.0.0.0 Safari/537.36'}
vacancies_data = []
client = MongoClient('127.0.0.1', 27017)
db = client['jobs']
vacancies = db.vacancies
vacancies_log = db.vacancies_log
salary_check = int(input(f'Введите фильтр для зарплаты:'))


def vacancies_to_db():
    search = list(vacancies.find({'link': vacancy_link}))
    if search:
        vacancies_log.insert_one({'Duplicate_insert': vacancy_link})
    else:
        vacancies.insert_one(vacancies_info)


def salary_print():
    for job in vacancies.find({
        '$or': [{'salary_min': {'$gt': salary_check}}, {'salary_max': {'$gt': salary_check}}]}
                              ):
        pprint(job)


def salary(data):
    if data:
        data = data.getText().replace('\u202f', ' ')
        data = re.sub(r'(\d)\s+(\d)', r'\1\2', data).replace(' –', '').split()
        salary_currency = data[2]
        if data[0] == 'до':
            salary_min = None
            salary_max = int(data[1])
        elif data[0] == 'от':
            salary_min = int(data[1])
            salary_max = None
        else:
            salary_min = int(data[0])
            salary_max = int(data[1])
    else:
        salary_min = None
        salary_max = None
        salary_currency = None
    return salary_min, salary_max, salary_currency


while url:
    response = requests.get(main_url + url, params=params, headers=headers)
    soup = bs(response.text, 'html.parser')
    vacancies_list = soup.find_all('div', {'class': 'vacancy-serp-item-body__main-info'})

    for vacancy in vacancies_list:
        vacancies_info = {}
        vacancy_anchor = vacancy.find('a')
        vacancy_name = vacancy_anchor.getText()
        vacancy_link = vacancy_anchor['href']
        vacancy_anchor = vacancy.find('div', {'class': 'vacancy-serp-item-company'}).find('a')
        vacancy_company = vacancy_anchor.getText().replace('\xa0', ' ')
        vacancy_anchor = vacancy.find('div', {'data-qa': 'vacancy-serp__vacancy-address'})
        vacancy_location = vacancy_anchor.getText()
        vacancy_anchor = vacancy.find('span', {'data-qa': 'vacancy-serp__vacancy-compensation'})
        vacancy_salary_min, vacancy_salary_max, vacancy_salary_currency = salary(vacancy_anchor)

        vacancies_info['vacancy'] = vacancy_name
        vacancies_info['link'] = vacancy_link
        vacancies_info['company'] = vacancy_company
        vacancies_info['location'] = vacancy_location
        vacancies_info['site'] = main_url
        vacancies_info['salary_min'] = vacancy_salary_min
        vacancies_info['salary_max'] = vacancy_salary_max
        vacancies_info['salary_currency'] = vacancy_salary_currency
        vacancies_data.append(vacancies_info)

        vacancies_to_db()

    url = soup.find('a', {'data-qa': 'pager-next'})
    if url:
        url = url['href']
    else:
        url = None

salary_print()
