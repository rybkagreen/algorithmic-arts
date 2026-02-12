import re
import structlog

log = structlog.get_logger()

# Регулярные выражения для парсинга финансирования
FUNDING_PATTERN = re.compile(
    r"(\d[\d\s]*(?:\.\d+)?)\s*(млн|млрд|тыс)?\s*(руб|рублей|\$|€|USD|EUR)?",
    re.IGNORECASE,
)

# Множители для конвертации
MULTIPLIERS = {
    "": 1,        # без суффикса → единицы
    "тыс": 1000,
    "млн": 1_000_000,
    "млрд": 1_000_000_000,
}

# Курсы валют (приблизительные)
CURRENCY_RATES = {
    "rub": 1.0,
    "рублей": 1.0,
    "rur": 1.0,
    "$": 90.0,
    "usd": 90.0,
    "€": 100.0,
    "eur": 100.0,
}


def parse_funding(text: str) -> dict | None:
    """
    Парсит сумму финансирования из текста.
    Возвращает: {"amount": int (копейки), "currency": str, "raw": str}
    """
    if not text:
        return None
        
    m = FUNDING_PATTERN.search(text)
    if not m:
        return None
        
    amount_str, unit, currency = m.groups()
    
    # Очищаем число от пробелов и запятых
    amount_clean = float(amount_str.replace(" ", "").replace(",", ""))
    
    # Применяем множитель
    multiplier = MULTIPLIERS.get(unit.lower() if unit else "", 1)
    amount_base = amount_clean * multiplier
    
    # Определяем валюту
    currency_clean = currency.lower() if currency else "rub"
    rate = CURRENCY_RATES.get(currency_clean, 1.0)
    
    # Конвертируем в копейки (RUB × 100)
    amount_kopeks = int(amount_base * rate * 100)
    
    return {
        "amount": amount_kopeks,
        "currency": "RUB",
        "raw": m.group(0),
    }