# Варианты def parse:
# С учетом 429 ошибки. Если ловим 429, то делаем time.sleep 1 минуту.
def parse() -> set[Any]:
    """Запускает парсинг avito."""
    items = []

    for url in settings.AVITO_URLS:
        pages_url = get_pages(url)
        for page_url in pages_url:
            while True:
                try:
                    base.get_random_sleep()
                    response = requests.get(page_url)
                    if response.status_code == 429:
                        logging.info(
                            "Получен статус 429: слишком много запросов. Ожидание 1 минуты...")
                        time.sleep(60)
                        continue

                    # Если запрос успешен, получаем товары
                    result = get_products(page_url)
                    items.append(result)
                    break  # Выходим из цикла, если запрос успешен

                except Exception as e:
                    logging.error(f"Ошибка при запросе к {page_url}: {e}")
                    break  # Выходим из цикла в случае других ошибок

        # Объединяем все найденные товары и удаляем дубликаты
        items = set(reduce(iconcat, items, []))
        logging.info(f"Avito: всего товаров: {len(items)}")

        if items:
            database.insert_items(items)
        else:
            logging.warning("Нет товаров для добавления в базу данных.")


    return items


# Для того, чтобы записывать товары в базу после прохода каждой страницы пагинации.
def parse() -> set[Any]:
    """Запускает парсинг avito."""
    for url in settings.AVITO_URLS:
        items = []  # Список для хранения товаров
        for page in get_pages(url):
            time.sleep(10)
            result = get_products(page)
            if result:
                items.extend(result)  # Добавляем элементы из result в items
                items = list(set(items))  # Преобразуем в set и обратно в list для удаления дубликатов
                # Вставляем данные в базу после парсинга каждой страницы
                if items:
                    database.insert_items(items)  # Запись в базу после обработки каждой страницы
                    logging.info(f"Добавлено товаров в базу: {len(items)}")
                    items.clear()  # Очищаем список после вставки, чтобы не добавлять дубликаты

        logging.info(f"Avito: всего товаров добавлено: {len(items)}")

        if not items:
            logging.warning("Нет товаров для добавления в базу данных.")

        return items


# Обычная
def parse() -> set[Any]:
    """Запускает парсинг avito."""
    items = []

    for url in settings.AVITO_URLS:
        pages_url = get_pages(url)
        for page_url in pages_url:
            base.get_random_sleep()
            logging.info(f"Запускаю страницу {page_url}")
            result = get_products(page_url)
            items.append(result)

        # Объединяем все найденные товары и удаляем дубликаты
        items = set(reduce(iconcat, items, []))
        logging.info(f"Avito: всего товаров: {len(items)}")

        if items:
            database.insert_items(items)
        else:
            logging.warning("Нет товаров для добавления в базу данных.")


    return items



# Чтобы получить отчет с учетом даты получения товара.
def gen_file():
    with closing(psycopg.connect(settings.PG_DSN)) as conn, closing(conn.cursor()) as cursor:
        # Запрашиваем данные из базы
        today = datetime.datetime.now().date()
        cursor.execute(
            'SELECT name, article, url, attrs '
            'FROM items '
            'WHERE DATE(created_at) >= %s',
            (today,)
        )
        data = cursor.fetchall()  # Получаем все строки
        # logging.info(data)
        # Проверяем, есть ли данные
        if not data:
            logging.info("Нет товаров для записи.")  # Сообщение, если товаров нет
            return

        # Установка временной зоны
        offset = datetime.timedelta(hours=3)
        tz = datetime.timezone(offset)

        now = datetime.datetime.now().astimezone(tz=tz)
        formatted_date = now.strftime("%Y%m%d-%H-%M")

        file_name = f'avito-{formatted_date}.xlsx'


attrs = {
                "price": price, # Цена
                # "price": int(product_card["contactBarInfo"]["price"]),  # Цена
                # "price": int(product_card["ga"][1]["currency_price"]),  # Цена
                # "availability": product["iva"]["BadgeBarStep"][0]["payload"]["badges"][0]["title"], # Доступность
                "availability": availability, # Доступность
                # "seller": product["iva"]["UserInfoStep"][0]["payload"]["profile"]["title"], # Продавец
                # "seller": product_card["contactBarInfo"]["seller"]["name"],  # Продавец
                "seller": seller,  # Продавец
                "region": product["location"]["name"], # Регион
                "promotion": promotion, # Продвижение
                "number_of_days_promotion": number_of_days_promotion, # Количество дней (продвижение)
                "promotion_type": promotion_type, # Тип продвижения
                "promotion_date": product["iva"]["DateInfoStep"][0]["payload"]["absolute"], # Дата продвижения
                "advertisement_date": product_card["item"]["sortFormatedDate"], # Дата объявления
                # "advertisement_number": product["id"], # Номер объявления - article
                "brand": product_card["ga"][1]["marka"], # Марка
                "model": product_card["ga"][1]["model"], # Модель
                "body_type": product_card["ga"][1]["tip_kuzova"], # Тип кузова
                "year_of_issue": product_card["ga"][1]["god_vypuska"], # Год выпуска
                "wheel_formula": product_card["ga"][1]["kolesnaya_formula"], # Колесная формула
                "condition": product_card["ga"][1]["condition"], # Состояние
                # "product_link": , # Ссылка на объявление - url
                "company_individual_vendor": product_card["contactBarInfo"]["publicProfileInfo"]["sellerName"], # Компания / частное лицо
}

# Проверяем наличие urlPath
item_url = product.get('urlPath')
if not item_url:
    # Пытаемся получить urlPath из описания
    item_url_description = product.get("iva", ).get("DescriptionStep", [])
    item_url = item_url_description[0].get("payload", ).get("urlPath")
else:
    logging.error(f"Не получен URL продукта {product}")
    continue

item_url = f"https://www.avito.ru{item_url}"
