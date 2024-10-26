import json
from dataclasses import dataclass
from typing import Iterable
import logging

import psycopg

from avito_scraper import settings


@dataclass
class Item:
    """Сущность товара."""

    name: str
    advertisement_number: int
    url: str
    attrs: dict


    def __eq__(self, other) -> bool:
        """Переопределенный метод для возможности формирования сетов товаров."""
        if isinstance(other, Item):
            return (self.advertisement_number,) == (
                other.advertisement_number,
            )
        return False


    def __hash__(self) -> int:
        """Переопределенный метод для возможности формирования сетов товаров."""
        return hash(self.advertisement_number)


def init_schema() -> None:
    """Инициализирует схему в базу данных."""
    with psycopg.connect(settings.PG_DSN) as connection, psycopg.ClientCursor(
        connection,
    ) as cursor:
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS items (
                id BIGINT GENERATED BY DEFAULT AS IDENTITY PRIMARY KEY,
                name TEXT NOT NULL,
                advertisement_number BIGINT UNIQUE NOT NULL,
                url TEXT NOT NULL,
                attrs JSONB NOT NULL,
                created_at TIMESTAMP DEFAULT NOW() NOT NULL
            );
        """)
        connection.commit()


def mogrify_items(cursor, items: Iterable[Item]):
    """Формирует список вставляемых значений в базу данных.
    Данный метод является значительно более производительным по сравению с cursor.executemany.
    """
    for item in items:
        yield cursor.mogrify(
            "(%s,%s,%s,%s)",
            (item.name, item.advertisement_number, item.url, json.dumps(item.attrs)),
        )


def insert_items(items: Iterable[Item]) -> None:
    """Заносит список товаров в базу данных."""
    logging.info(f"Попытка вставить {len(items)} товаров в базу данных.")

    if not items:
        logging.error("Ошибка: список товаров пуст.")
        return  # Завершение выполнения функции, если список пуст

    with psycopg.connect(settings.PG_DSN) as connection, psycopg.ClientCursor(
        connection,
    ) as cursor:
        # Удаляем дубликаты
        unique_data = {item.advertisement_number: item for item in items}.values()  # item.advertisement_number — это уникальный идентификатор

        # Формируем строки для вставки
        insert_values = []
        for item in unique_data:
            # Преобразуем attrs в строку JSON
            attrs_json = json.dumps(item.attrs) if isinstance(item.attrs, dict) else item.attrs
            insert_values.append((item.name, item.advertisement_number, item.url, attrs_json))

        try:
            cursor.executemany(
                """INSERT INTO items (name, advertisement_number, url, attrs) 
                VALUES (%s, %s, %s, %s)
                ON CONFLICT (advertisement_number) DO UPDATE SET
                name = EXCLUDED.name,
                url = EXCLUDED.url,
                attrs = EXCLUDED.attrs""",
                insert_values
            )
        except Exception as e:
            logging.error(f"Ошибка при вставке данных: {e}")
            connection.rollback()  # Откат транзакции в случае ошибки
        else:
            connection.commit()  # Подтверждение транзакции только в случае успеха
