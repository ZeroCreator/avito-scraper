import secrets

from avito_scraper import settings


def get_proxy():
    """Получает словарь со случайным прокси-адресом для http-запросов."""
    if not settings.PROXIES:
        return None
    return secrets.choice(settings.PROXIES)
