from datetime import date

from app.services.renewal import renewal_bucket, renewal_window_days


def test_renewal_window_days() -> None:
    assert renewal_window_days(date(2026, 6, 28), today=date(2026, 4, 29)) == 60


def test_renewal_bucket() -> None:
    assert renewal_bucket(-1) == "expired"
    assert renewal_bucket(30) == "0-30"
    assert renewal_bucket(60) == "31-60"
    assert renewal_bucket(90) == "61-90"
    assert renewal_bucket(91) == "future"
