"""Engine tính toán học phí theo tín chỉ học phí (TCHP) và quy tắc HUST."""

from __future__ import annotations

from datetime import date
from decimal import Decimal
from typing import Any


def calculate_subject_tuition(
    tuition_credits: Decimal | float | int | str,
    price_per_credit: int,
) -> int:
    """Tính học phí môn học = tuition_credits * price_per_credit.

    Làm tròn xuống đến đồng (int). Tuyệt đối không dùng float trong tính toán tiền tệ.
    """
    tc_dec = Decimal(str(tuition_credits))
    rate_dec = Decimal(str(price_per_credit))
    return int(tc_dec * rate_dec)


def resolve_tuition_rate(
    rates: list[Any],
    cohort: str | None,
    major: str | None,
    effective_date: date | None = None,
) -> Any | None:
    """Chọn bản ghi đơn giá khớp nhất cho sinh viên theo thứ tự ưu tiên:

    1. Khớp cả cohort và major
    2. Khớp cohort, major là None (áp dụng chung cho khóa)
    3. cohort là None, khớp major (áp dụng chung cho ngành)
    4. Cả cohort và major đều là None (đơn giá chung toàn trường)
    """
    if effective_date is not None:
        rates = [
            rate
            for rate in rates
            if rate.effective_from <= effective_date
            and (rate.effective_to is None or rate.effective_to >= effective_date)
        ]
    if not rates:
        return None

    # Mức 1: Khớp cả cohort và major
    if cohort and major:
        for r in rates:
            if getattr(r, "cohort", None) == cohort and getattr(r, "major", None) == major:
                return r

    # Mức 2: Khớp cohort, major is None
    if cohort:
        for r in rates:
            if getattr(r, "cohort", None) == cohort and getattr(r, "major", None) is None:
                return r

    # Mức 3: cohort is None, khớp major
    if major:
        for r in rates:
            if getattr(r, "cohort", None) is None and getattr(r, "major", None) == major:
                return r

    # Mức 4: Cả 2 đều None
    for r in rates:
        if getattr(r, "cohort", None) is None and getattr(r, "major", None) is None:
            return r

    return None
