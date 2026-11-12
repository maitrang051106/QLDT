from __future__ import annotations

from datetime import date

from sqlalchemy.orm import Session

from app.core.error_codes import ErrorCode
from app.core.exceptions import AppError, field_error
from app.core.timeutil import now_vn, to_vn
from app.dto.common import Page, PageParams
from app.dto.tuition.tuition import (
    InvoiceGenerateRequest,
    InvoiceGenerateResult,
    PaymentCreateRequest,
    ReceiptDto,
    TuitionInvoiceDto,
    TuitionInvoiceItemDto,
    TuitionPaymentDto,
    TuitionRateCreateRequest,
    TuitionRateResponse,
    TuitionRateUpdateRequest,
    TuitionSummaryDto,
)
from app.entity.auth.student import Student
from app.entity.auth.user import Role, User
from app.entity.catalog.semester import Semester
from app.entity.catalog.subject import Subject
from app.entity.tuition.receipt import Receipt
from app.entity.tuition.tuition_invoice import InvoiceStatus, TuitionInvoice
from app.entity.tuition.tuition_invoice_item import TuitionInvoiceItem
from app.entity.tuition.tuition_payment import TuitionPayment
from app.entity.tuition.tuition_rate import TuitionRate
from app.repository.auth.user_repository import StudentRepository
from app.repository.catalog.semester_repository import SemesterRepository
from app.repository.tuition.tuition_repository import TuitionRepository
from app.service.catalog.semester_service import SemesterService
from app.service.tuition.tuition_calculator import (
    calculate_subject_tuition,
    resolve_tuition_rate,
)
from app.service.tuition.vietnamese_words import number_to_vietnamese_words


class TuitionService:
    def __init__(self, db: Session) -> None:
        self.db = db
        self.repo = TuitionRepository(db)
        self.students = StudentRepository(db)
        self.semesters = SemesterRepository(db)

    def _ensure_rate_range_available(
        self,
        semester_id: int,
        cohort: str | None,
        major: str | None,
        effective_from: date,
        effective_to: date | None,
        exclude_rate_id: int | None = None,
    ) -> None:
        self.repo.lock_semester(semester_id)
        if effective_to is not None and effective_to < effective_from:
            raise AppError(
                ErrorCode.VALIDATION_ERROR,
                details=[field_error("effectiveTo", "Ngày kết thúc phải sau ngày bắt đầu")],
            )
        for rate in self.repo.list_rates(semester_id):
            if rate.id == exclude_rate_id or rate.cohort != cohort or rate.major != major:
                continue
            overlaps = (rate.effective_to is None or effective_from <= rate.effective_to) and (
                effective_to is None or rate.effective_from <= effective_to
            )
            if overlaps:
                raise AppError(
                    ErrorCode.DUPLICATE_CODE,
                    details=[
                        field_error(
                            "effectiveFrom",
                            "Khoảng hiệu lực bị trùng với đơn giá cùng học kỳ, khóa và ngành",
                        )
                    ],
                )

    # ==================== TUITION RATES ====================
    def list_rates(self, semester_id: int | None = None) -> list[TuitionRateResponse]:
        entities = self.repo.list_rates(semester_id)
        return [
            TuitionRateResponse(
                id=r.id,
                semester_id=r.semester_id,
                cohort=r.cohort,
                major=r.major,
                effective_from=r.effective_from,
                effective_to=r.effective_to,
                price_per_credit=r.price_per_credit,
                description=r.description,
                created_at=to_vn(r.created_at),
            )
            for r in entities
        ]

    def create_rate(self, request: TuitionRateCreateRequest) -> TuitionRateResponse:
        semester = self.semesters.get_by_id(request.semester_id)
        if semester is None:
            raise AppError(
                ErrorCode.NOT_FOUND, details=[field_error("semesterId", "Học kỳ không tồn tại")]
            )

        effective_from = request.effective_from or semester.start_date
        effective_to = request.effective_to or semester.end_date
        self._ensure_rate_range_available(
            request.semester_id,
            request.cohort,
            request.major,
            effective_from,
            effective_to,
        )
        self.repo.mark_invoices_stale(request.semester_id)
        entity = TuitionRate(
            semester_id=request.semester_id,
            cohort=request.cohort,
            major=request.major,
            effective_from=effective_from,
            effective_to=effective_to,
            price_per_credit=request.price_per_credit,
            description=request.description,
        )
        self.repo.add_rate(entity)
        self.db.commit()
        return TuitionRateResponse(
            id=entity.id,
            semester_id=entity.semester_id,
            cohort=entity.cohort,
            major=entity.major,
            effective_from=entity.effective_from,
            effective_to=entity.effective_to,
            price_per_credit=entity.price_per_credit,
            description=entity.description,
            created_at=to_vn(entity.created_at),
        )

    def update_rate(self, rate_id: int, request: TuitionRateUpdateRequest) -> TuitionRateResponse:
        entity = self.repo.get_rate_by_id(rate_id)
        if entity is None:
            raise AppError(ErrorCode.NOT_FOUND)

        effective_from = request.effective_from or entity.effective_from
        effective_to = (
            request.effective_to
            if "effective_to" in request.model_fields_set
            else entity.effective_to
        )
        self._ensure_rate_range_available(
            entity.semester_id,
            request.cohort,
            request.major,
            effective_from,
            effective_to,
            exclude_rate_id=entity.id,
        )
        self.repo.mark_invoices_stale(entity.semester_id)
        entity.cohort = request.cohort
        entity.major = request.major
        entity.effective_from = effective_from
        entity.effective_to = effective_to
        entity.price_per_credit = request.price_per_credit
        entity.description = request.description
        self.db.commit()
        return TuitionRateResponse(
            id=entity.id,
            semester_id=entity.semester_id,
            cohort=entity.cohort,
            major=entity.major,
            effective_from=entity.effective_from,
            effective_to=entity.effective_to,
            price_per_credit=entity.price_per_credit,
            description=entity.description,
            created_at=to_vn(entity.created_at),
        )

    def delete_rate(self, rate_id: int) -> None:
        entity = self.repo.get_rate_by_id(rate_id)
        if entity is None:
            raise AppError(ErrorCode.NOT_FOUND)
        self.repo.mark_invoices_stale(entity.semester_id)
        self.repo.delete_rate(entity)
        self.db.commit()

    # ==================== INVOICE CALCULATION / GENERATION ====================
    def generate_single_invoice(
        self,
        student: Student,
        semester: Semester,
        rates: list[TuitionRate],
        registered_subjects: list[Subject],
    ) -> TuitionInvoice | None:
        """Tạo mới hoặc tính lại hóa đơn cho một sinh viên."""
        existing = self.repo.get_invoice_by_student_semester_for_update(student.id, semester.id)
        if existing and (existing.amount_paid > 0 or existing.status == InvoiceStatus.CANCELLED):
            return None  # Không tính lại hóa đơn đã có giao dịch nộp tiền

        items_to_add, total_tuition = self._build_invoice_items(
            student, semester, rates, registered_subjects
        )
        amount_due = total_tuition

        if existing is None:
            invoice = TuitionInvoice(
                student_id=student.id,
                semester_id=semester.id,
                total_tuition=total_tuition,
                amount_due=amount_due,
                amount_paid=0,
                status=InvoiceStatus.UNPAID,
                is_stale=False,
                items=items_to_add,
            )
            self.repo.add_invoice(invoice)
        else:
            existing.total_tuition = total_tuition
            existing.amount_due = amount_due
            existing.is_stale = False
            self.repo.delete_invoice_items(existing.id)
            existing.items = items_to_add
            invoice = existing

        return invoice

    @staticmethod
    def _build_invoice_items(
        student: Student,
        semester: Semester,
        rates: list[TuitionRate],
        registered_subjects: list[Subject],
    ) -> tuple[list[TuitionInvoiceItem], int]:
        rate = resolve_tuition_rate(
            rates, student.cohort, student.major, effective_date=semester.start_date
        )
        if registered_subjects and rate is None:
            raise AppError(
                ErrorCode.TUITION_RATE_NOT_FOUND,
                message=f"Chưa có đơn giá học phí cho học kỳ {semester.semester_code}",
            )

        items: list[TuitionInvoiceItem] = []
        total = 0
        if rate is not None:
            for subject in registered_subjects:
                amount = calculate_subject_tuition(
                    subject.effective_tuition_credits, rate.price_per_credit
                )
                total += amount
                items.append(
                    TuitionInvoiceItem(
                        subject_id=subject.id,
                        subject_code=subject.subject_code,
                        subject_name=subject.name,
                        credits=subject.credits,
                        tuition_credits=subject.effective_tuition_credits,
                        price_per_credit=rate.price_per_credit,
                        amount=amount,
                    )
                )
        return items, total

    def generate_invoices(self, request: InvoiceGenerateRequest) -> InvoiceGenerateResult:
        """Tạo/tính lại hóa đơn hàng loạt bằng truy vấn gom nhóm tránh N+1."""
        semester = self.semesters.get_by_id(request.semester_id)
        if semester is None:
            raise AppError(
                ErrorCode.NOT_FOUND, details=[field_error("semesterId", "Học kỳ không tồn tại")]
            )

        rates = self.repo.list_rates(request.semester_id)
        if not rates and not request.student_id:
            raise AppError(
                ErrorCode.TUITION_RATE_NOT_FOUND,
                message=f"Chưa có bảng đơn giá học phí cho học kỳ {semester.semester_code}",
            )

        students = self.repo.list_students_for_update(request.student_id)
        if request.student_id is not None and not students:
            raise AppError(ErrorCode.NOT_FOUND)
        student_ids = [student.id for student in students]
        student_subjects_map = self.repo.get_registered_students_and_subjects(
            request.semester_id, student_id=request.student_id
        )
        existing_by_student = {
            invoice.student_id: invoice
            for invoice in self.repo.list_invoices_for_students_for_update(
                request.semester_id, student_ids
            )
        }
        total_generated = 0
        total_skipped = 0
        invoices_to_add: list[TuitionInvoice] = []
        invoices_to_update: list[TuitionInvoice] = []
        invoice_items_to_add: list[tuple[TuitionInvoice, list[TuitionInvoiceItem]]] = []

        for student in students:
            subjects = student_subjects_map.get(student.id, [])
            items, total_tuition = self._build_invoice_items(student, semester, rates, subjects)
            amount_due = total_tuition
            existing = existing_by_student.get(student.id)
            if existing and (
                existing.amount_paid > 0 or existing.status == InvoiceStatus.CANCELLED
            ):
                total_skipped += 1
                continue
            if existing is None:
                invoice = TuitionInvoice(
                    student_id=student.id,
                    semester_id=semester.id,
                    total_tuition=total_tuition,
                    amount_due=amount_due,
                    amount_paid=0,
                    status=InvoiceStatus.UNPAID,
                    is_stale=False,
                )
                invoices_to_add.append(invoice)
            else:
                invoice = existing
                invoice.total_tuition = total_tuition
                invoice.amount_due = amount_due
                invoice.is_stale = False
                invoices_to_update.append(invoice)
            invoice_items_to_add.append((invoice, items))
            total_generated += 1

        self.repo.delete_invoice_items_for_invoices([item.id for item in invoices_to_update])
        self.db.add_all(invoices_to_add)
        self.db.add_all(invoices_to_update)
        self.db.flush()
        for invoice, items in invoice_items_to_add:
            for item in items:
                item.invoice_id = invoice.id
        self.db.add_all(item for _, items in invoice_items_to_add for item in items)

        self.db.commit()
        return InvoiceGenerateResult(
            total_generated=total_generated,
            total_skipped=total_skipped,
            message=f"Đã tạo/cập nhật {total_generated} hóa đơn ({total_skipped} hóa đơn bỏ qua do đã nộp tiền)",
        )

    # ==================== STUDENT TUITION VIEW ====================
    def get_student_tuition(self, user: User, semester_id: int | None = None) -> TuitionInvoiceDto:
        student = self.students.get_by_user_id(user.id)
        if student is None:
            raise AppError(ErrorCode.FORBIDDEN)

        if semester_id is None:
            semester_id = SemesterService(self.db).get_current().id

        invoice = self.repo.get_invoice(student.id, semester_id)
        semester = self.semesters.get_by_id(semester_id)
        if semester is None:
            raise AppError(
                ErrorCode.NOT_FOUND, details=[field_error("semesterId", "Học kỳ không tồn tại")]
            )

        if invoice is None:
            subj_map = self.repo.get_registered_students_and_subjects(semester_id, student.id)
            subjects = subj_map.get(student.id, [])
            if subjects:
                rates = self.repo.list_rates(semester_id)
                if not rates:
                    raise AppError(ErrorCode.TUITION_RATE_NOT_FOUND)
                self.generate_single_invoice(student, semester, rates, subjects)
                self.db.commit()
                invoice = self.repo.get_invoice(student.id, semester_id)

        if invoice is None:
            return TuitionInvoiceDto(
                id=0,
                student_id=student.id,
                student_code=student.student_code,
                student_name=student.full_name,
                cohort=student.cohort,
                major=student.major,
                semester_id=semester_id,
                semester_code=semester.semester_code,
                total_tuition=0,
                amount_due=0,
                amount_paid=0,
                balance=0,
                status="UNPAID",
                is_stale=False,
                items=[],
                payments=[],
                created_at=now_vn(),
                updated_at=now_vn(),
            )

        items_dtos = [
            TuitionInvoiceItemDto(
                id=item.id,
                subject_id=item.subject_id,
                subject_code=item.subject_code,
                subject_name=item.subject_name,
                credits=item.credits,
                tuition_credits=item.tuition_credits,
                price_per_credit=item.price_per_credit,
                amount=item.amount,
            )
            for item in invoice.items
        ]

        payments_dtos = [
            TuitionPaymentDto(
                id=p.id,
                amount=p.amount,
                idempotency_key=p.idempotency_key,
                payment_method=p.payment_method,
                paid_at=to_vn(p.paid_at),
                receipt_no=p.receipt.receipt_no if p.receipt else None,
            )
            for p in invoice.payments
        ]

        balance = max(0, invoice.amount_due - invoice.amount_paid)
        return TuitionInvoiceDto(
            id=invoice.id,
            student_id=student.id,
            student_code=student.student_code,
            student_name=student.full_name,
            cohort=student.cohort,
            major=student.major,
            semester_id=invoice.semester_id,
            semester_code=invoice.semester.semester_code if invoice.semester else "",
            total_tuition=invoice.total_tuition,
            amount_due=invoice.amount_due,
            amount_paid=invoice.amount_paid,
            balance=balance,
            status=invoice.status.value,
            is_stale=invoice.is_stale,
            items=items_dtos,
            payments=payments_dtos,
            created_at=to_vn(invoice.created_at),
            updated_at=to_vn(invoice.updated_at),
        )

    # ==================== IDEMPOTENT PAYMENT ====================
    def make_payment(self, user: User, request: PaymentCreateRequest) -> ReceiptDto:
        """Thực hiện thanh toán giả lập học phí idempotent và phát hành biên lai bất biến."""
        student = self.students.get_by_user_id(user.id)
        if student is None:
            raise AppError(ErrorCode.FORBIDDEN)

        existing_payment = self.repo.get_payment_by_key(student.id, request.idempotency_key)
        if existing_payment and existing_payment.receipt:
            return self._receipt_dto(existing_payment.receipt, student)

        semester_id = SemesterService(self.db).get_current().id

        invoice = self.repo.get_invoice_by_student_semester_for_update(student.id, semester_id)
        if invoice is None:
            raise AppError(ErrorCode.INVOICE_NOT_FOUND)

        existing_payment = self.repo.get_payment_by_key(student.id, request.idempotency_key)
        if existing_payment and existing_payment.receipt:
            return self._receipt_dto(existing_payment.receipt, student)

        if invoice.status == InvoiceStatus.PAID:
            raise AppError(ErrorCode.INVOICE_ALREADY_PAID)
        if invoice.status == InvoiceStatus.CANCELLED:
            raise AppError(ErrorCode.INVOICE_CANCELLED)

        # Thanh toán một lần: luôn nộp đúng toàn bộ số tiền còn phải nộp.
        amount = invoice.amount_due - invoice.amount_paid
        if amount <= 0:
            raise AppError(
                ErrorCode.VALIDATION_ERROR,
                details=[field_error("invoice", "Hóa đơn không có số tiền cần thanh toán")],
            )

        payment = TuitionPayment(
            invoice_id=invoice.id,
            student_id=student.id,
            amount=amount,
            idempotency_key=request.idempotency_key,
            payment_method="SIMULATED",
        )
        self.repo.add_payment(payment)

        invoice.amount_paid += amount
        invoice.status = InvoiceStatus.PAID

        semester = self.semesters.get_by_id(semester_id)
        semester_code = semester.semester_code if semester else "2026.1"
        receipt_no = self.repo.next_receipt_number(semester_id, semester_code)

        snapshot_items = [
            {
                "subjectCode": item.subject_code,
                "subjectName": item.subject_name,
                "credits": item.credits,
                "tuitionCredits": str(item.tuition_credits),
                "pricePerCredit": item.price_per_credit,
                "amount": item.amount,
            }
            for item in invoice.items
        ]
        receipt_data = {
            "receiptNo": receipt_no,
            "studentCode": student.student_code,
            "fullName": student.full_name,
            "cohort": student.cohort or "",
            "major": student.major or "",
            "semesterCode": semester_code,
            "semesterName": semester.name if semester else "",
            "items": snapshot_items,
            "totalTuition": invoice.total_tuition,
            "amountDue": invoice.amount_due,
            "paymentAmount": amount,
            "cumulativePaid": invoice.amount_paid,
            "balanceRemaining": max(0, invoice.amount_due - invoice.amount_paid),
            "amountInWords": number_to_vietnamese_words(amount),
            "paymentMethod": "Thanh toán giả lập",
        }

        receipt = Receipt(
            receipt_no=receipt_no,
            payment=payment,
            student_id=student.id,
            invoice_id=invoice.id,
            amount=amount,
            receipt_data=receipt_data,
        )
        self.repo.add_receipt(receipt)
        self.db.commit()

        return self._receipt_dto(receipt, student)

    @staticmethod
    def _receipt_dto(receipt: Receipt, student: Student) -> ReceiptDto:
        return ReceiptDto(
            id=receipt.id,
            receipt_no=receipt.receipt_no,
            payment_id=receipt.payment_id,
            student_id=receipt.student_id,
            student_code=student.student_code,
            student_name=student.full_name,
            invoice_id=receipt.invoice_id,
            amount=receipt.amount,
            amount_in_words=number_to_vietnamese_words(receipt.amount),
            issued_at=to_vn(receipt.issued_at),
            receipt_data=receipt.receipt_data,
        )

    # ==================== RECEIPTS QUERIES ====================
    def list_student_receipts(self, user: User, semester_id: int | None = None) -> list[ReceiptDto]:
        student = self.students.get_by_user_id(user.id)
        if student is None:
            raise AppError(ErrorCode.FORBIDDEN)

        entities = self.repo.list_receipts_by_student(student.id, semester_id)
        return [
            ReceiptDto(
                id=r.id,
                receipt_no=r.receipt_no,
                payment_id=r.payment_id,
                student_id=r.student_id,
                student_code=student.student_code,
                student_name=student.full_name,
                invoice_id=r.invoice_id,
                amount=r.amount,
                amount_in_words=number_to_vietnamese_words(r.amount),
                issued_at=to_vn(r.issued_at),
                receipt_data=r.receipt_data,
            )
            for r in entities
        ]

    def get_receipt(self, user: User, receipt_id: int) -> ReceiptDto:
        receipt = self.repo.get_receipt_by_id(receipt_id)
        if receipt is None:
            raise AppError(ErrorCode.NOT_FOUND)

        if user.role == Role.STUDENT:
            student = self.students.get_by_user_id(user.id)
            if student is None or receipt.student_id != student.id:
                raise AppError(ErrorCode.FORBIDDEN)
        elif user.role != Role.ADMIN:
            raise AppError(ErrorCode.FORBIDDEN)

        return ReceiptDto(
            id=receipt.id,
            receipt_no=receipt.receipt_no,
            payment_id=receipt.payment_id,
            student_id=receipt.student_id,
            student_code=receipt.student.student_code if receipt.student else None,
            student_name=receipt.student.full_name if receipt.student else None,
            invoice_id=receipt.invoice_id,
            amount=receipt.amount,
            amount_in_words=number_to_vietnamese_words(receipt.amount),
            issued_at=to_vn(receipt.issued_at),
            receipt_data=receipt.receipt_data,
        )

    # ==================== ADMIN INVOICES & SUMMARY ====================
    def list_admin_invoices(
        self,
        semester_id: int,
        status: str | None,
        student_code: str | None,
        paging: PageParams,
    ) -> Page[TuitionInvoiceDto]:
        st_enum = InvoiceStatus(status) if status else None
        invoices, total = self.repo.list_invoices(
            semester_id=semester_id,
            status=st_enum,
            student_code=student_code,
            offset=paging.offset,
            limit=paging.size,
        )

        dtos = [
            TuitionInvoiceDto(
                id=inv.id,
                student_id=inv.student_id,
                student_code=inv.student.student_code if inv.student else "",
                student_name=inv.student.full_name if inv.student else "",
                cohort=inv.student.cohort if inv.student else None,
                major=inv.student.major if inv.student else None,
                semester_id=inv.semester_id,
                semester_code=inv.semester.semester_code if inv.semester else "",
                total_tuition=inv.total_tuition,
                amount_due=inv.amount_due,
                amount_paid=inv.amount_paid,
                balance=max(0, inv.amount_due - inv.amount_paid),
                status=inv.status.value,
                is_stale=inv.is_stale,
                items=[],
                payments=[],
                created_at=to_vn(inv.created_at),
                updated_at=to_vn(inv.updated_at),
            )
            for inv in invoices
        ]
        return Page.of(dtos, paging, total)

    def get_summary(self, semester_id: int) -> TuitionSummaryDto:
        semester = self.semesters.get_by_id(semester_id)
        data = self.repo.get_summary(semester_id)
        return TuitionSummaryDto(
            semester_id=semester_id,
            semester_code=semester.semester_code if semester else "",
            total_invoices=data["totalInvoices"],
            total_amount_due=data["totalAmountDue"],
            total_amount_paid=data["totalAmountPaid"],
            total_balance=data["totalBalance"],
            paid_count=data["paidCount"],
            partially_paid_count=data["partiallyPaidCount"],
            unpaid_count=data["unpaidCount"],
        )
