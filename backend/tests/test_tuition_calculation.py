from datetime import date
from decimal import Decimal

from app.service.tuition.tuition_calculator import (
    calculate_subject_tuition,
    resolve_tuition_rate,
)
from app.service.tuition.vietnamese_words import number_to_vietnamese_words


def test_number_to_vietnamese_words():
    assert number_to_vietnamese_words(0) == "Không đồng"
    assert number_to_vietnamese_words(12345000) == "Mười hai triệu ba trăm bốn mươi lăm nghìn đồng"
    assert number_to_vietnamese_words(15000000) == "Mười lăm triệu đồng"
    assert number_to_vietnamese_words(1005000) == "Một triệu không trăm lẻ năm nghìn đồng"
    assert number_to_vietnamese_words(21000) == "Hai mươi mốt nghìn đồng"
    assert number_to_vietnamese_words(100000000) == "Một trăm triệu đồng"


def test_calculate_subject_tuition_decimal_and_rounding():
    assert calculate_subject_tuition(3, 450000) == 1350000
    assert calculate_subject_tuition(Decimal("1.5"), 450000) == 675000
    assert calculate_subject_tuition(Decimal("3.6"), 478125) == 1721250
    assert calculate_subject_tuition(Decimal("1.33"), 10000) == 13300


class FakeRate:
    def __init__(self, cohort, major, price):
        self.cohort = cohort
        self.major = major
        self.price = price
        self.effective_from = date.min
        self.effective_to = None


def test_resolve_tuition_rate_priority():
    r_general = FakeRate(None, None, 450000)
    r_cohort = FakeRate("K66", None, 480000)
    r_major = FakeRate(None, "CNTT", 520000)
    r_specific = FakeRate("K66", "CNTT", 550000)
    r_general.effective_from = date(2026, 1, 1)
    r_general.effective_to = date(2026, 12, 31)
    r_specific.effective_from = date(2026, 1, 1)
    r_specific.effective_to = date(2026, 6, 30)
    r_cohort.effective_to = date(2026, 6, 30)
    r_major.effective_to = date(2026, 6, 30)

    rates = [r_general, r_cohort, r_major, r_specific]

    assert resolve_tuition_rate(rates, "K66", "CNTT").price == 550000
    assert resolve_tuition_rate(rates, "K66", "CoKhi").price == 480000
    assert resolve_tuition_rate(rates, "K67", "CNTT").price == 520000
    assert resolve_tuition_rate(rates, "K67", "Dien").price == 450000
    assert resolve_tuition_rate(rates, "K66", "CNTT", date(2026, 7, 1)).price == 450000
