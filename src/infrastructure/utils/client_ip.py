"""
Утилиты для получения IP клиента.

Поддерживает reverse proxy (Traefik, Nginx) через заголовки.
"""

from fastapi import Request

# Доверенные proxy (внутренние сети)
TRUSTED_PROXIES = {
    "127.0.0.1",
    "10.0.0.0/8",
    "172.16.0.0/12",
    "192.168.0.0/16",
}


def get_client_ip(request: Request) -> str:
    """
    Получение IP клиента с поддержкой reverse proxy.
    
    Приоритет заголовков:
    1. X-Real-IP (Nginx) — один IP, не цепочка
    2. X-Forwarded-For (Traefik, HAProxy) — цепочка: client, proxy1, proxy2
    3. request.client.host (fallback)
    
    :param request: FastAPI request
    :return: IP клиента
    """
    # X-Real-IP (один IP, не цепочка)
    real_ip = request.headers.get("X-Real-IP")
    if real_ip:
        return real_ip.split(",")[0].strip()
    
    # X-Forwarded-For (цепочка: client, proxy1, proxy2)
    forwarded = request.headers.get("X-Forwarded-For")
    if forwarded:
        # Первый IP в цепочке — клиент
        client_ip = forwarded.split(",")[0].strip()
        
        # ⚠️ В production: проверить что запрос от доверенного proxy
        # if request.client.host in TRUSTED_PROXIES:
        return client_ip
    
    # Fallback — прямое подключение
    return request.client.host or "unknown"
