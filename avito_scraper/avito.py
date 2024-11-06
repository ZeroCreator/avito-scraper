from __future__ import annotations

import time
import json
from typing import Any

import logging
from functools import reduce
from operator import iconcat

from avito_scraper.proxy import get_proxy, get_socproxy
from avito_scraper import base, database, settings


STARTWITH_DATA = '<script type="mime/invalid" data-mfe-state="true">'
ENDWITH_DATA = '</script></div>'


def get_pages(url):
    page_urls = []

    proxy = get_proxy()
    response = base.get_response(url, proxy)

    # Получаем количество страниц пагинации
    page_count = base.get_page_count(response)

    for page in range(page_count + 1):   # Добавляем еще одну страницу на всякий случай если во время парсинга были добавлены товары и страниц стало больше
        page_url = f"{url}&p={page + 1}"
        logging.info(f"Добавляем страницу: {page_url}")
        page_urls.append(page_url)

    return page_urls


def get_products_pages(url: str):
    logging.info(f"Запускаю страницу {url}")
    response_text = base.repeat_parsing(url)
    # Получаем строку с данными
    json_string = base.get_json_string(response_text, STARTWITH_DATA, ENDWITH_DATA, 2)
    # Декодируем строку и получаем JSON
    products_data = json.loads(json_string)

    if not products_data:
        logging.info("JSON не сформирован")
        return []

    products_pages = base.find_value_by_key(products_data, "items")

    if not products_pages:
        logging.info("Товаров items в JSON нет")
        return []

    return products_pages


def get_products(products_pages):
    items = []
    for product in products_pages:
        # Проверяем наличие urlPath
        item_url_data = product.get('urlPath')
        if item_url_data:
            item_url = f"https://www.avito.ru{item_url_data}"
        else:
            logging.info(f"Нет 'urlPath' у товара {product}")
            continue

        logging.info(f"Переходим на страницу товара {item_url}")
        product_data = base.get_json(item_url)
        if not product_data:
            logging.info("Товара нет")
            continue

        try:
            product_card = base.find_value_by_key(product_data, "buyerItem")
            # Дата объявления
            advertisement_date = product_card.get("item", {}).get("sortFormatedDate", [])
            # Цена
            price = product.get("priceDetailed", {}).get("value", [])
            # Продавец
            seller = product_card.get("contactBarInfo", {}).get("seller", {}).get("name", [])
            # Доступность
            date_availability = product.get("iva", {}).get("BadgeBarStep", [])
            availability_payload = date_availability[0].get("payload", {}).get(
                "badges", []) if len(date_availability) > 0 else 0
            availability = availability_payload[0].get("title", []) if len(
                availability_payload) > 0 else []

            if "Реальный адрес" in availability:
                availability = availability_payload[2].get("title", []) if len(
                availability_payload) > 0 else []

            # Продвижение. Получаем значение продвижения (promotion). Если его нет, то возвращаем 0.
            date_info_step = product.get("iva", {}).get("DateInfoStep", [])
            vas = date_info_step[1].get("payload", {}).get("vas", []) if len(
                date_info_step) > 1 else 0
            promotion = vas[0].get("title", []) if len(vas) > 0 else []

            if promotion and promotion != "Продвинуто":
                promotion = []

            # Количество дней (продвижение)
            number_of_days_promotion = vas[0].get("slug", 0) if len(vas) > 0 else []
            # Тип продвижения
            promotion_type = vas[1].get("title", []) if len(vas) > 1 else []

            if promotion_type and promotion_type == "Выделено":
                promotion_type = []

            # Дата продвижения
            promotion_date_infostep = product.get("iva", {}).get("DateInfoStep", [])
            promotion_date = promotion_date_infostep[0].get("payload", {}).get(
                "absolute", []) if len(promotion_date_infostep) > 0 else []

            # Марка
            characteristics = product_card.get("ga", [])
            brand = characteristics[1].get("marka", []) if len(characteristics) > 1 else []
            # Модель
            model = characteristics[1].get("model", []) if len(characteristics) > 1 else []
            # Тип кузова
            body_type = characteristics[1].get("tip_kuzova", []) if len(characteristics) > 1 else []
            # Год выпуска
            year_of_issue = characteristics[1].get("god_vypuska", []) if len(
                characteristics) > 1 else []
            # Колесная формула
            wheel_formula = characteristics[1].get("kolesnaya_formula", []) if len(
                characteristics) > 1 else []
            # Состояние
            condition = characteristics[1].get("condition", []) if len(
                characteristics) > 1 else []
            # Компания / частное лицо
            company_individual_vendor = product_card.get("contactBarInfo", {}).get(
                "publicProfileInfo", {}).get("sellerName", [])
            # Регион
            region = product.get("location", {}).get("name", [])

            attrs = {
                "advertisement_date": advertisement_date,  # Дата объявления
                "price": price, # Цена
                "seller": seller,  # Продавец
                "availability": availability, # Доступность
                "promotion": promotion, # Продвижение
                "number_of_days_promotion": number_of_days_promotion, # Количество дней (продвижение)
                "promotion_type": promotion_type, # Тип продвижения
                "promotion_date": promotion_date, # Дата продвижения
                "brand": brand, # Марка
                "model": model, # Модель
                "body_type": body_type, # Тип кузова
                "year_of_issue": year_of_issue, # Год выпуска
                "wheel_formula": wheel_formula, # Колесная формула
                "condition": condition, # Состояние
                "company_individual_vendor": company_individual_vendor, # Компания / частное лицо
                "region": region,  # Регион
            }

            item = database.Item(
                name=product["title"],
                advertisement_number=product["id"],
                url=f"https://www.avito.ru{product['urlPath']}",
                attrs=attrs,
            )
            logging.info(item)
            items.append(item)

        except Exception as e:
            logging.error(f"Ошибка при парсинге страницы товара: {e}")

    return items


def parse() -> set[Any]:
    """Запускает парсинг avito."""
    items = []
    products_pages = []

    for url in settings.AVITO_URLS:
        logging.info(f"Собираем товары с каталога {url}")
        pages_url = get_pages(url)
        for page_url in pages_url:
            result = get_products_pages(page_url)

            if result:
                products_pages.extend(result)
                logging.info(f"Со страницы собрано {len(result)} товаров")
            else:
                logging.info(f"Товаров со страницы {page_url} не найдено")
                continue

        logging.info(f"Всего товаров: {len(products_pages)}")
        items = get_products(products_pages)
        # Объединяем все найденные товары и удаляем дубликаты
        items = set(reduce(iconcat, items, []))
        logging.info(f"Avito: всего товаров: {len(items)}")

        if items:
            database.insert_items(items)
        else:
            logging.warning("Нет товаров для добавления в базу данных")


    return items
