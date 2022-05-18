import requests
import json

ticker = input(f'Введите тикер:')
start_day = input(f'Введите начало отслеживания (YYYY-MM-DD):')
end_day = input(f'Введите конец отслеживания (YYYY-MM-DD):')
# установите свой key
key = '...'

url = 'https://data.nasdaq.com/api/v3/datasets/WIKI/'+ticker+'/data.json?start_date='+start_day+'&end_date='+end_day+'?api_key='+key
data = requests.get(url)

with open('api_data.json', 'w') as f:
    json.dump(data.json(), f)
