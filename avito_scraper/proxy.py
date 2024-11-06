import secrets
import logging

from avito_scraper import settings

PROXIES=[
    'http://0.0.0.0:9001',
    'http://0.0.0.0:9002',
    'http://0.0.0.0:9003',
    'http://0.0.0.0:9004',
    'http://0.0.0.0:9005',
    'http://0.0.0.0:9006',
    'http://0.0.0.0:9007',
    'http://0.0.0.0:9008',
    'http://0.0.0.0:9009'
]

def get_proxy():
    """Получает словарь со случайным прокси-адресом для http-запросов."""
    if not PROXIES:
        logging.info('None')
        return None
    return secrets.choice(PROXIES)


def get_socproxy():
    """Получает словарь со случайным socks5-адресом для http-запросов."""
    SOCKS_PROXIES = [
        'socks5://89.110.92.16:33400',
        'socks5://109.172.85.93:33400',
        'socks5://109.172.88.150:33400',
        'socks5://109.172.88.22:33400',
        'socks5://45.8.230.58:33400',
        'socks5://193.104.57.75:33400'
    ]
    return secrets.choice(SOCKS_PROXIES)
