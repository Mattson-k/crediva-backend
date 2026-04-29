from datetime import date
from typing import Optional


def renewal_window_days(expiration_date: date, today: Optional[date] = None) -> int:
    today = today or date.today()
    return (expiration_date - today).days


def renewal_bucket(days: int) -> str:
    if days < 0:
        return "expired"
    if days <= 30:
        return "0-30"
    if days <= 60:
        return "31-60"
    if days <= 90:
        return "61-90"
    return "future"
