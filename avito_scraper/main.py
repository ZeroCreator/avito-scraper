import asyncio
import sys
from pathlib import Path

sys.path.append(str(Path(__name__).parent.parent))

import logging

from avito_scraper import database, settings, create_and_send_file, avito

logging.basicConfig(
    datefmt="%Y-%m-%d %H:%M:%S",
    format="%(asctime)s %(levelname)-s %(message)s",
    level=logging.INFO,
)


async def main() -> None:
    logging.info("Инициализирую схему данных")
    database.init_schema()

    logging.info(f"Запускаю парсинг каждые {settings.INTERVAL_MINUTES} минут")
    while True:
        await asyncio.wait(
            [
                asyncio.create_task(avito.parse()),
            ],
        )
        #create_and_send_file.gen_file()
        logging.info(f"Парсинг завершен, ожидаю {settings.INTERVAL_MINUTES} минут")
        await asyncio.sleep(settings.INTERVAL_MINUTES * 60)


if __name__ == "__main__":
    asyncio.run(main())
