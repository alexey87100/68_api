import os
import requests
import random
import time
import pprint

from dotenv import load_dotenv


load_dotenv()

DOG_ENDPOINT = 'https://random.dog/woof.json'
FOX_ENDPOINT = 'https://randomfox.ca/floof/'
POOLING_TIME = 1
START_OFFSET = 0


class Bot:
    """Класс реализующий отправку и чтение сообщений ТГ. """

    TELEGRAM_BOT_TOKEN = os.getenv('TG_BOT_TOKEN')
    MY_CHAT_ID = os.getenv('MY_CHAT_ID')
    ENDPOINT = f'https://api.telegram.org/bot{ TELEGRAM_BOT_TOKEN }/'

    @classmethod
    def send_message(cls, message):
        """Отправка текстового сообщения в ТГ чат. """
        endpoint = f'{cls.ENDPOINT}sendMessage'
        params = {
            "chat_id": cls.MY_CHAT_ID,
            'text': message
        }
        try:
            response = requests.post(endpoint, params)
            response.raise_for_status()
        except Exception as error:
            print(f'Ошибка при отправке сообщения в ТГ: {error}')
        else:
            print('Успешно отправлено сообщение в ТГ')

    @classmethod
    def send_photo(cls, image_path):
        """Отправка картинки в ТГ чат."""
        endpoint = f'{cls.ENDPOINT}sendPhoto'
        params = {
            'chat_id': cls.MY_CHAT_ID,
            'caption': "Вот ваша очередная картиночка!",
        }
        try:
            files = {
                'photo': open(image_path, 'rb'),
            }
            response = requests.post(endpoint, params, files=files)
            response.raise_for_status()
        except Exception as error:
            cls.send_message(f'Ошибка при отправке картинки в ТГ: { error }')
        else:
            print('Успешно отправлена картинка в ТГ')
    
    @classmethod
    def get_updates(cls, offset):
        """Проверка пула сообщений на серверах ТГ."""
        endpoint = f'{cls.ENDPOINT}getUpdates'
        params = {
            'offset': offset,
        }
        try:
            response = requests.get(endpoint, params=params)
            response.raise_for_status()
            return response
        except Exception as error:
            cls.send_message(f'Ошибка при проверка пула сообщений: { error }')


def get_api_answer(ENDPOINT):
    """Получение ответа от API."""
    try:
        response = requests.get(ENDPOINT)
        response.raise_for_status()
    except Exception as error:
        Bot.send_message(f'Ошибка при соверешнии запроса'
                         f'к API с картинками: { error }')
    return response


def get_image(ENDPOINT) -> str:
    """Получение картинки от API стороннего ресурса. """

    try:
        image_url = get_api_answer(ENDPOINT).json()
        if ENDPOINT == FOX_ENDPOINT:
            image_url = image_url['image']
            image_format = image_url.split('.')[-1]
            image_name = f"fox/{random.randint(1, 1000000)}.{image_format}"
        elif ENDPOINT == DOG_ENDPOINT:
            image_url = image_url['url']
            image_format = image_url.split('.')[-1]
            image_name = f"dog/{random.randint(1, 1000000)}.{image_format}"
        image = get_api_answer(image_url).content
        with open(image_name, 'wb') as fd:
            fd.write(image)
            return image_name
    except Exception as error:
        Bot.send_message(f'Ошибка при скачивании картинки: { error }')


COMMANDS = {
    '/send_fox': FOX_ENDPOINT,
    '/send_dog': DOG_ENDPOINT,
}


def main():
    """Основной метод работы бота. Опрос пула сообщений."""
    try:
        offset = START_OFFSET
        while True:
            messages = Bot.get_updates(offset).json()['result']
            if messages:
                offset = int(messages[-1]['update_id']) + 1
                for message in messages:
                    if message['message'].get('text') is not None:
                        text = message['message'].get('text')
                        if text not in COMMANDS.keys():
                            Bot.send_message("Я пока не знаю этой команды")
                        else:
                            Bot.send_photo(get_image(COMMANDS[text]))
                    else:
                        Bot.send_message("Я могу обрабатывать только текстовые сообщения")
            
            time.sleep(POOLING_TIME)
    except Exception as error:
        print(f'Бот неожиданно завершил работу: { error }')


if __name__ == '__main__':
    # print(get_api_answer(FOX_ENDPOINT).json())

    # get_image(DOG_ENDPOINT) # Скачать картинку запросом к API
    # Bot.send_message("Привет!") # Отправить сообщение в бота
    # Bot.send_photo('fox/50706.jpg') # Отправить фото в бота
    # print(Bot.get_updates(396728176).json())
    # pprint.pprint(Bot.get_updates(396728160).json()) # Посмотреть на пул сообщений от бота.
    main() # Основной цикл проверки пула сообщений и отправки ответа на них