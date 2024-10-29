from __future__ import annotations

import time
import requests
import logging
import json
import urllib.parse
from functools import reduce
from operator import iconcat

from avito_scraper.proxy import get_proxy
from avito_scraper import database, settings


HEADERS = {
    'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36',
    'Cookie': 'luri=krasnodar; srv_id=-RauT6nTheIE_YyL.PbR79mgSLabjd58OEtHIguAWhckRY0jXJ4iKagydaby-Iz3_6KQ4HUUN1CgI06x6dsO1.DBCwmXE-M6_25z7xISuZOo1r602l2ONpCY80kch3pn8=.web; gMltIuegZN2COuSe=EOFGWsm50bhh17prLqaIgdir1V0kgrvN; u=32q5bwbe.qap9h3.srhm9zmuee00; buyer_laas_location=640760; _gcl_au=1.1.1100649811.1730034436; ma_cid=1897102441730034436; uxs_uid=63d18290-9464-11ef-b119-83ca41565890; f=5.0c4f4b6d233fb90636b4dd61b04726f147e1eada7172e06c47e1eada7172e06c47e1eada7172e06c47e1eada7172e06cb59320d6eb6303c1b59320d6eb6303c1b59320d6eb6303c147e1eada7172e06c8a38e2c5b3e08b898a38e2c5b3e08b890df103df0c26013a7b0d53c7afc06d0b2ebf3cb6fd35a0ac0df103df0c26013a8b1472fe2f9ba6b92e1d4a3283ded56a90d83bac5e6e82bd59c9621b2c0fa58f915ac1de0d03411231a1058e37535dce34d62295fceb188df88859c11ff008953de19da9ed218fe2d50b96489ab264ede992ad2cc54b8aa87fde300814b1e855d50b96489ab264ed3de19da9ed218fe23de19da9ed218fe23de19da9ed218fe2b5b87f59517a23f280a995c83bf64175352c31daf983fa077a7b6c33f74d335c76ff288cd99dba461f91c771e1e458a0cd0833ebb6c2bf424a6ac852c96eb120cef5a27e990a49cd17c7721dca45217bc7a454ea5bfb17efdeeb76342c551eefe2415097439d404746b8ae4e81acb9fa786047a80c779d5146b8ae4e81acb9fa96520d3a86f5312a8db57d0f7c7638d42da10fb74cac1eabb3ae333f3b35fe91de6c39666ae9b0d71c77f048ad687d8e7ce5970e4b0456c9; ft="s/3cVCN7MXBc+rZywGSffgkTLDW3KgTlAU6TlcjrhLvyVVsFHpJy1UTVyHpdglgcs6Npoz1zLS6ygoBHo7CLcnEk7ZyFdiqquoicb4UoJXM5BnPooTS06b6WvorU0aADYTFESkHSFzEID/uQXulKQnGFtZOwRHlTTnFLNr9jTko6v0TRggKwx83WGibEOZSR"; redirectMav=1; v=1730110698; luri=rostov-na-donu; buyer_location_id=652000; SEARCH_HISTORY_IDS=0; dfp_group=5; sx=H4sIAAAAAAAC%2F5zSTU5zOwzG8b1k3EHsxHbMbhI7bqEtX4WWAzp7v%2BqVeMX4bOCnvx77JwGKAJOGz2ijwhCuUMXB0YcgpIefdE0P6X1c6ni6nW71CT%2B%2BLm%2FjetlDiY%2Fl6%2BP4%2BE1pl2Z6ACkZVABo3SU0mp1q9LBGbs5dFEPCGzcUn9tkXnepIAwEFyqtliKlFidRGsQ992Zlm1zWXaq5CpKEgY2ojOCBHjFq9e7F6Fd%2B3p%2BXU36Pk7fnNp%2BuYS%2Bvy2159pcDn2%2Flr6yN7s3MzObCoazElXXKmEVdKJuJ66%2F8dkR7p0NM1nr%2BXL6vsOz3cN3Xy%2Fl8eM1%2FZMyKd7l3tmDBojYKaM6l9dyLFGdraLhpjSz%2FyxYKKEPm1ArTaZDd70fDm4Jt2xnXXRochaf5EBYJgomzVMtsPJtz%2Ftesh0u0GwbG91Vxvh2n3460%2BOcJX%2FVx%2BSs3orbukpcGIL1E2JQJGT1XvOeKA7rUbc1wl%2BtsUotSy9DQLYYzmkZX6JmbbvgNgVLX9b8AAAD%2F%2F6HKr6iFAwAA; abp=0; ma_id=4921116551730113458075; ma_ss_64a8dba6-67f3-4fe4-8625-257c4adae014=7509977231730111497.3.1730113473.11',
}

CAPCHA = 'Доступ ограничен: проблема с IP'
INITIAL_DATA = 'window.__initialData__ = '


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


def repeat_parsing(url):
    response_text = ""
    logging.info(url)
    for attempt in range(5):
        proxy = get_proxy()
        logging.info(f"Используем прокси: {proxy}")
        time.sleep(5)
        try:
            response = requests.get(
                url,
                headers=HEADERS,
                timeout=60,
                proxies={
                    "http": proxy,
                    "https": proxy,
                },
            )

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


def get_json(url):
    response_text = repeat_parsing(url)
    try:
        # Достаем из всей страницы только строку window.__initialData__
        json_string = response_text.split('window.__initialData__ = ')[1].split('window.__mfe__')[0]
        # Обрезаем кавычки и последний символ ";"
        json_string = json_string.strip()[1:-2]

        # Декодируем полученные данные
        decoded_json_string = urllib.parse.unquote(json_string)
        # Получаем JSON
        data = json.loads(decoded_json_string)

        return data
    except Exception as e:
        logging.error(f"Ошибка при парсинге товара: {e}")


def get_pages(url):
    page_urls = []  # по умолчанию возвращаем 0, если параметр отсутствует
    for page in range(5):
        page_url = f"{url}&p={page + 1}"
        print(f"Текущая страница: {page_url}")
        page_urls.append(page_url)
    print(page_urls)
    return page_urls


def get_products(url: str):
    products_data = get_json(url)
    if not products_data:
        logging.info("Товаров products_data нет")
        return []

    products = find_value_by_key(products_data, "items")

    if not products:
        logging.info("Товаров products нет")
        return []

    items = []
    for product in products:
        if product.get('urlPath'):
            item_url = f"https://www.avito.ru{product['urlPath']}"
        else:
            logging.info("Нет product['urlPath']")
            continue

        logging.info(item_url)
        product_data = get_json(item_url)
        if not product_data:
            logging.info("Товара нет")
            continue
        try:
            product_card = find_value_by_key(product_data, "buyerItem")

            date_info_step = product.get("iva", {}).get("DateInfoStep", [])
            vas = date_info_step[1].get("payload", {}).get("vas", []) if len(date_info_step) > 1 else []
            promotion = vas[0].get("title", 0) if len(vas) > 0 else 0

            attrs = {
                "price": int(product["priceDetailed"]["value"]), # Цена
                # "price": int(product_card["contactBarInfo"]["price"]),  # Цена
                # "price": int(product_card["ga"][1]["currency_price"]),  # Цена
                "availability": product["iva"]["BadgeBarStep"][0]["payload"]["badges"][0]["title"], # Доступность
                #"seller": product["iva"]["UserInfoStep"][0]["payload"]["profile"]["title"], # Продавец
                "seller": product_card["contactBarInfo"]["seller"]["name"],  # Продавец
                "region": product["location"]["name"], # Регион
                "promotion": promotion, # Продвижение
                "promotion_date": product["iva"]["DateInfoStep"][0]["payload"]["absolute"], # Дата продвижения
                "advertisement_date": product["iva"]["DateInfoStep"][0]["payload"]["absolute"], # Дата объявления
                "advertisement_number": product["id"], # Номер объявления - article
                "brand": product_card["ga"][1]["marka"], # Марка
                "model": product["title"].replace(product_card["ga"][1]["marka"], ""), # Модель
                "body_type": product_card["ga"][1]["tip_kuzova"], # Тип кузова
                "year_of_issue": product_card["ga"][1]["god_vypuska"], # Год выпуска
                "wheel_formula": product_card["ga"][1]["kolesnaya_formula"], # Колесная формула
                "condition": product_card["ga"][1]["condition"], # Состояние
                # "product_link": , # Ссылка на объявление - url
                "company_individual_vendor": product_card["contactBarInfo"]["publicProfileInfo"]["sellerName"], # Компания / частное лицо

            }

            item = database.Item(
                name=product["title"],
                article=product["id"],
                url=f"https://www.avito.ru{product['urlPath']}",
                attrs=attrs,
            )
            logging.info(item)
            items.append(item)
        except Exception as e:
            logging.error(f"Ошибка при парсинге страницы товара: {e}")

    return items


def parse() -> None:
    """Запускает парсинг avito."""
    items = []
    for url in settings.AVITO_URLS:
        pages = get_pages(url)
        for page in pages:
            result = get_products(page)
            items.append(result)

    items = set(reduce(iconcat, items, []))
    logging.info(f"Avito: всего товаров: {len(items)}")

    if items:
        database.insert_items(items)
    else:
        logging.warning("Нет товаров для добавления в базу данных.")
