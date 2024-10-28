import asyncio
import sys
import time
from pathlib import Path

sys.path.append(str(Path(__name__).parent.parent))

import logging

from avito_scraper import database, settings, create_and_send_file, avito, proxy

logging.basicConfig(
    datefmt="%Y-%m-%d %H:%M:%S",
    format="%(asctime)s %(levelname)-s %(message)s",
    level=logging.INFO,
)


def main() -> None:
    logging.info("Инициализирую схему данных")
    database.init_schema()

    logging.info(f"Запускаю парсинг")

    items = avito.parse(),
    # Проверяем, собраны ли товары
    if items and items[0] is not None:  # Если список не пуст
        logging.info(f"Найдено {len(items)} товаров, генерирую файл...")
        create_and_send_file.gen_file()
    else:
        logging.warning("Товары не найдены, файл не будет создан.")

    logging.info(f"Парсинг завершен")


if __name__ == "__main__":
    main()
