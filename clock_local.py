"""Datas de negócio em São Paulo, inclusive quando a hospedagem usa UTC."""
from datetime import datetime
from zoneinfo import ZoneInfo

def now_local():
    return datetime.now(ZoneInfo('America/Sao_Paulo')).replace(tzinfo=None)

def today_local():
    return now_local().date()
