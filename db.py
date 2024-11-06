"""Модуль для работы с бд.
Содержит функции для:
- подсчета общего количества товаров;
- удаления всех товаров из таблицы и
- удаления самой таблицы."""

import psycopg
import logging

table_name = "items"
dsn = "postgresql://postgres:postgres@127.0.0.1:5432/postgres"

def select_items(table_name, dsn):
    """Функция для подсчета общего количества товаров."""
    with psycopg.connect(dsn) as conn:
        with conn.cursor() as cur:
            try:
                count_query = cur.execute(f'SELECT COUNT(*) FROM {table_name};')
                cur.execute(count_query)
                logging.info(f'В таблице {count_query} позиций.')

            except Exception as e:
                logging.error(f"Таблица отсутствует: {e}")

select_items("items", "postgresql://postgres:postgres@127.0.0.1:5432/postgres")


def truncate_table(table_name, dsn):
    """Функция для удаления всех товаров из таблицы."""
    with psycopg.connect(dsn) as conn:
        with conn.cursor() as cur:
            truncate_table = cur.execute(f'TRUNCATE TABLE {table_name};')
            cur.execute(truncate_table)
            logging.info(f'Все данные из таблицы {table_name} успешно удалены.')

# truncate_table("items", "postgresql://postgres:postgres@127.0.0.1:5432/postgres")


def drop_table(table_name, dsn):
    """Функция для удаления самой таблицы."""
    # Проверка на допустимые символы в имени таблицы
    if not table_name.isidentifier():
        logging.error(f'Недопустимое имя таблицы: {table_name}')
        return

    with psycopg.connect(dsn) as conn:
        with conn.cursor() as cur:
            # Формируем SQL-запрос для удаления таблицы
            drop_query = f'DROP TABLE IF EXISTS {table_name};'
            cur.execute(drop_query)

            logging.info(f'Таблица {table_name} успешно удалена.')

#drop_table("items", "postgresql://postgres:postgres@127.0.0.1:5432/postgres")
