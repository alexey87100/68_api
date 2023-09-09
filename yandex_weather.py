import os

from dotenv import load_dotenv
import requests
import pprint

load_dotenv()

ENDPOINT = 'https://api.weather.yandex.ru/v2/informers/'
PARAMS = {
   'lat': 55.751562,
   'lon': 37.619969,
   'lang': 'ru_RU',
}
HEADERS = {
    'X-Yandex-API-Key': os.getenv('YA_WEATHER_TOKEN')
}

response = requests.get(ENDPOINT, headers=HEADERS, params=PARAMS)


pprint.pprint(response.json(), indent=1)
