from __future__ import annotations

from datetime import date
from typing import Any

from pydantic import Field

from app.dto.common import CamelModel, VNDateTime


class TuitionRateResponse(CamelModel):
    id: int
    semester_id: int
    cohort: str | None = None
    major: str | None = None
    effective_from: date
    effective_to: date | None = None
    price_per_credit: int
    description: str | None = None
    created_at: VNDateTime


class TuitionRateCreateRequest(CamelModel):
    semester_id: int
    cohort: str | None = None
    major: str | None = None
    effective_from: date | None = None
    effective_to: date | None = None
    price_per_credit: int = Field(..., gt=0)
    description: str | None = None


class TuitionRateUpdateRequest(CamelModel):
    cohort: str | None = None
    major: str | None = None
    effective_from: date | None = None
    effective_to: date | None = None
    price_per_credit: int = Field(..., gt=0)
    description: str | None = None


class TuitionInvoiceItemDto(CamelModel):
    id: int
    subject_id: int
    subject_code: str
    subject_name: str
    credits: int
    tuition_credits: float
    price_per_credit: int
    amount: int


class TuitionPaymentDto(CamelModel):
    id: int
    amount: int
    idempotency_key: str
    payment_method: str
    paid_at: VNDateTime
    receipt_no: str | None = None


class TuitionInvoiceDto(CamelModel):
    id: int
    student_id: int
    student_code: str | None = None
    student_name: str | None = None
    cohort: str | None = None
    major: str | None = None
    semester_id: int
    semester_code: str | None = None
    total_tuition: int
    amount_due: int
    amount_paid: int
    balance: int
    status: str
    is_stale: bool
    items: list[TuitionInvoiceItemDto] = Field(default_factory=list)
    payments: list[TuitionPaymentDto] = Field(default_factory=list)
    created_at: VNDateTime
    updated_at: VNDateTime


class PaymentCreateRequest(CamelModel):
    idempotency_key: str = Field(..., min_length=1, max_length=64)


class ReceiptDto(CamelModel):
    id: int
    receipt_no: str
    payment_id: int
    student_id: int
    student_code: str | None = None
    student_name: str | None = None
    invoice_id: int
    amount: int
    amount_in_words: str | None = None
    issued_at: VNDateTime
    receipt_data: dict[str, Any]


class InvoiceGenerateRequest(CamelModel):
    semester_id: int
    student_id: int | None = None


class InvoiceGenerateResult(CamelModel):
    total_generated: int
    total_skipped: int
    message: str


class TuitionSummaryDto(CamelModel):
    semester_id: int
    semester_code: str | None = None
    total_invoices: int
    total_amount_due: int
    total_amount_paid: int
    total_balance: int
    paid_count: int
    partially_paid_count: int
    unpaid_count: int
