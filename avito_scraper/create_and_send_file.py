from ftplib import FTP
import psycopg
from avito_scraper import settings
import xlsxwriter
import datetime
from pathlib import Path


def gen_file():
    conn = psycopg.connect(settings.PG_DSN)
    cursor = conn.cursor()

    cursor.execute('SELECT article, name, attrs, created_at, url FROM items')
    data = cursor.fetchall()

    offset = datetime.timedelta(hours=3)
    tz = datetime.timezone(offset)

    now = datetime.datetime.now().astimezone(tz=tz)
    formatted_date = now.strftime("%Y%m%d-%H-%M")

    file_name = f'avito-{formatted_date}.xlsx'

    workbook = xlsxwriter.Workbook(f'/tmp/{file_name}')
    worksheet = workbook.add_worksheet()

    worksheet.write(0, 0, 'article')
    worksheet.write(0, 1, 'name')
    worksheet.write(0, 2, 'url')
    worksheet.write(0, 3, 'seller')
    worksheet.write(0, 4, 'price')
    worksheet.write(0, 5, 'brand')
    worksheet.write(0, 6, 'model')
    worksheet.write(0, 7, 'body_type')
    worksheet.write(0, 8, 'year_of_issue')
    worksheet.write(0, 9, 'wheel_formula')
    worksheet.write(0, 10, 'condition')
    worksheet.write(0, 11, 'availability')
    worksheet.write(0, 12, 'promotion')
    worksheet.write(0, 13, 'promotion_date')
    worksheet.write(0, 14, 'advertisement_date')
    worksheet.write(0, 15, 'advertisement_number')
    worksheet.write(0, 16, 'company_individual_vendor')
    worksheet.write(0, 17, 'region')

    workbook.close()

    cursor.execute('DELETE FROM items')
    conn.commit()
    conn.close()

    ftp = FTP(settings.FTP_HOST, user=settings.FTP_USER, passwd=settings.FTP_PASS)

    with open(f'/tmp/{file_name}', 'rb') as file:
        ftp.storbinary(f'STOR {file_name}', file)

    ftp.quit()

    for p in Path("/tmp").glob("*.xlsx"):
        p.unlink()
