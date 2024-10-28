import os

PG_DSN = os.getenv("PG_DSN", "postgresql://postgres:postgres@127.0.0.1:5432/postgres")

AVITO_URLS = os.getenv("AVITO_URLS", "")
if AVITO_URLS:
    AVITO_URLS = AVITO_URLS.split(",")

PROXIES = os.getenv("PROXIES", "")
if PROXIES:
    PROXIES = PROXIES.replace(" ", "").split(",")

FTP_HOST = os.getenv("FTP_HOST", "")
FTP_USER = os.getenv("FTP_USER", "")
FTP_PASS = os.getenv("FTP_PASS", "")
