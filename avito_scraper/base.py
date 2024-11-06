"""Модуль с набором вспомогательных функций для парсинга Avito."""

import random
import time
import json
import urllib.parse
import requests
import logging
from bs4 import BeautifulSoup

from avito_scraper.proxy import get_proxy, get_socproxy
from avito_scraper import headers

HEADERS = headers.HEADERS
PROXIES='http://0.0.0.0:9001,http://0.0.0.0:9002,http://0.0.0.0:9003,http://0.0.0.0:9004,http://0.0.0.0:9005,http://0.0.0.0:9006,http://0.0.0.0:9007,http://0.0.0.0:9008,http://0.0.0.0:9009'
CAPCHA = 'Доступ ограничен: проблема с IP'
INITIAL_DATA = 'window.__initialData__ = '


def get_response(url, proxy):
    response = requests.get(
        url,
        headers=HEADERS,
        timeout=60,
        proxies={
            "http": proxy,
            "https": proxy,
        },
    )
    return response


def get_random_sleep():
    delay = random.uniform(30, 60)
    logging.info(f"Спим : {delay}")
    return time.sleep(delay)


def repeat_parsing(url):
    response_text = ""
    for attempt in range(5):
        proxy = get_proxy()
        logging.info(f"Используем прокси: {proxy}")
        get_random_sleep()

        try:
            response = get_response(url, proxy)
            logging.info(f"Статус код: {response.status_code}")

            # Проверяем полученный статус кода
            if response.status_code == 200:
                response_text = response.text

                # Проверяем на отсутствие блокировки
                if (
                        CAPCHA not in response_text and
                        INITIAL_DATA in response_text
                ):
                    logging.info(f"Страница найдена.")
                    break
                else:
                    logging.info(f"Блокировка страницы {url}. Повторяю парсинг.")
            else:
                logging.warning(
                    f"Ошибка получения страницы {url}. Статус код: {response.status_code}.")

        except requests.RequestException as e:
            logging.error(f"Ошибка запроса: {e}. Продолжаем с следующим прокси.")

    # Проверка на успешность парсинга
    if not response_text or CAPCHA in response_text:
        logging.info(f"Блокировка страницы {url}. Пропускаем товар.")
        return None

    return response_text


def get_page_count(response):
    """Функция для получения количества страниц пагинации."""

    soup = BeautifulSoup(response.text, 'html.parser')
    select_page = soup.select('[aria-label="Пагинация"] ul')
    if "..." in select_page[0].text:
        page_count = select_page[0].text.split('...')[1]
        logging.info(f"Всего страниц: {page_count}")
    else:
        page_count = select_page[0].text
        page_count = [len(page_count)][0]
        logging.info(f"Всего страниц: {page_count}")

    return int(page_count)


def find_value_by_key(data, target_key):
    """Функция для получения значения по ключу во вложенных словарях."""
    if isinstance(data, dict):
        for key, value in data.items():
            if key == target_key:
                return value
            # Рекурсивный вызов для вложенных словарей
            result = find_value_by_key(value, target_key)
            if result is not None:
                return result
    elif isinstance(data, list):
        for item in data:
            result = find_value_by_key(item, target_key)
            if result is not None:
                return result
    return None


def get_json_string(response_text, start_data, end_data, start_index):
    return response_text.split(start_data)[start_index].split(end_data)[0]


def get_json(url):
    response_text = repeat_parsing(url)
    try:
        # Достаем из всей страницы только строку window.__initialData__
        json_string = response_text.split('window.__initialData__ = ')[1].split('window.__mfe__')[0]
        # Обрезаем кавычки и последний символ ";"
        json_string = json_string.strip()[1:-2]
        # Декодируем строку и получаем JSON
        data = get_decoder_json(json_string)

        return data
    except Exception as e:
        logging.error(f"Ошибка при парсинге товара: {e}")


def get_decoder_json(json_string):
    """Функция для декодирования данных и получения JSON."""
    decoded_json_string = urllib.parse.unquote(json_string)

    return json.loads(decoded_json_string)


def write_data_txt(data, file_name):
    """Функция для записи текста в файл."""
    with open(f'{file_name}.text', mode='w') as f:
        f.write(data)


def write_data_json(data, file_name):
    # Запись словаря в файл в формате JSON
    with open(f'{file_name}.json', mode='w') as f:
        json.dump(data, f, indent=4)  # indent=4 для форматирования
