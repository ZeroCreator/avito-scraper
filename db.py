import psycopg
import logging


# def truncate_table(table_name, dsn):
#     with psycopg.connect(dsn) as conn:
#         with conn.cursor() as cur:
#             cur.execute('SELECT * FROM items;')
#             # cur.execute(f'TRUNCATE TABLE {table_name};')
#             # print(f'Все данные из таблицы {table_name} успешно удалены.')
#             data = cur.fetchall()
#             if not data:
#                 print("Нет товаров для записи.")  # Сообщение, если товаров нет
#             print(data)
#
# truncate_table("items", "postgresql://postgres:postgres@127.0.0.1:5432/postgres")


def drop_table(table_name, dsn):
    with psycopg.connect(dsn) as conn:
        with conn.cursor() as cur:
            cur.execute(f'DROP TABLE IF EXISTS {table_name};')
            print(f'Таблица {table_name} успешно удалена.')


# Пример использования
drop_table("items", "postgresql://postgres:postgres@127.0.0.1:5432/postgres")
