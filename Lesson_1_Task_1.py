import requests
from pprint import pprint
import json

user = input(f'Введите имя пользователя:')
url = 'https://api.github.com/users/'+user+'/repos'
repo = []
data = requests.get(url)

# pprint(data.json())

with open('repos_data_'+user+'.json', 'w') as f:
    json.dump(data.json(), f)

for i in data.json():
    repo.append(i['name'])

print(repo)


