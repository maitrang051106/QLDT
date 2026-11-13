from datetime import date
from decimal import Decimal

from sqlalchemy import func, select

from app.entity.auth.lecturer import Lecturer
from app.entity.auth.student import Student
from app.entity.auth.user import Role, User
from app.entity.catalog.course_section import CourseSection
from app.entity.catalog.room import Room
from app.entity.catalog.semester import Semester
from app.entity.catalog.subject import Subject
from app.entity.registration.registration import Registration
from app.entity.tuition.receipt import Receipt
from app.entity.tuition.tuition_payment import TuitionPayment
from app.entity.tuition.tuition_rate import TuitionRate
from app.security.password import hash_password
from tests.conftest import login


def _tuition_world(db_session):
    semester = Semester(
        semester_code="2026.1",
        name="Học kỳ kiểm thử",
        start_date=date(2026, 9, 7),
        end_date=date(2027, 1, 18),
        num_weeks=20,
    )
    student = db_session.scalars(select(Student)).one()
    student.cohort = "K66"
    student.major = "CNTT"
    lecturer = db_session.scalars(select(Lecturer)).one()
    room = Room(room_code="TUITION-101", capacity=40)
    subject = Subject(
        subject_code="TUI101",
        name="Môn học học phí",
        credits=3,
        tuition_credits=Decimal("1.5"),
    )
    db_session.add_all([semester, room, subject])
    db_session.flush()

    section = CourseSection(
        section_code="TUI-01",
        subject_id=subject.id,
        semester_id=semester.id,
        lecturer_id=lecturer.id,
        room_id=room.id,
        day_of_week=2,
        start_period=1,
        end_period=2,
        start_week=1,
        end_week=20,
        max_capacity=40,
        current_enrollment=1,
    )
    rate = TuitionRate(
        semester_id=semester.id,
        cohort="K66",
        major="CNTT",
        effective_from=semester.start_date,
        effective_to=semester.end_date,
        price_per_credit=10000,
    )
    db_session.add_all([section, rate])
    db_session.flush()
    db_session.add(Registration(student_id=student.id, section_id=section.id))
    db_session.commit()
    return {
        "semester": semester,
        "student": student,
        "rate": rate,
        "subject": subject,
    }


def test_student_payment_is_idempotent_and_receipt_pdf_is_available(client, db_session):
    world = _tuition_world(db_session)
    student_headers = login(client, "sv1", "Sv@12345")
    invoice_response = client.get(
        f"/api/tuition/me?semesterId={world['semester'].id}", headers=student_headers
    )
    assert invoice_response.status_code == 200
    assert invoice_response.json()["totalTuition"] == 15000
    assert invoice_response.json()["items"][0]["tuitionCredits"] == 1.5

    payment_body = {"idempotencyKey": "tuition-payment-key-1"}
    payment_response = client.post(
        "/api/tuition/me/payments", json=payment_body, headers=student_headers
    )
    assert payment_response.status_code == 201, payment_response.text
    receipt = payment_response.json()
    repeated = client.post("/api/tuition/me/payments", json=payment_body, headers=student_headers)
    assert repeated.status_code == 201
    assert repeated.json()["id"] == receipt["id"]
    assert repeated.json()["receiptNo"] == receipt["receiptNo"]

    pdf_response = client.get(f"/api/receipts/{receipt['id']}/pdf", headers=student_headers)
    assert pdf_response.status_code == 200
    assert pdf_response.headers["content-type"] == "application/pdf"
    assert receipt["receiptNo"].encode() in pdf_response.content
    assert pdf_response.content.startswith(b"%PDF-")
    assert "filename*=UTF-8''" in pdf_response.headers["content-disposition"]
    assert db_session.scalar(select(func.count(TuitionPayment.id))) == 1
    assert db_session.scalar(select(func.count(Receipt.id))) == 1
    receipts = client.get(
        f"/api/receipts/me?semesterId={world['semester'].id}", headers=student_headers
    )
    assert receipts.status_code == 200
    assert [item["id"] for item in receipts.json()["items"]] == [receipt["id"]]

    # Thanh toán một lần: nộp đúng toàn bộ số phải nộp, hóa đơn chuyển sang PAID.
    assert receipt["amount"] == 15000
    paid_invoice = client.get(
        f"/api/tuition/me?semesterId={world['semester'].id}", headers=student_headers
    ).json()
    assert paid_invoice["status"] == "PAID"
    assert paid_invoice["balance"] == 0
    assert paid_invoice["amountPaid"] == 15000
    assert "installments" not in paid_invoice


def test_tuition_permissions_and_payment_limits(client, db_session):
    world = _tuition_world(db_session)
    student_headers = login(client, "sv1", "Sv@12345")
    admin_headers = login(client, "admin", "Admin@123")
    lecturer_headers = login(client, "gv1", "Gv@12345")

    invoice = client.get(
        f"/api/tuition/me?semesterId={world['semester'].id}", headers=student_headers
    )
    assert invoice.status_code == 200
    assert invoice.json()["balance"] == 15000

    paid = client.post(
        "/api/tuition/me/payments",
        json={"idempotencyKey": "pay-full"},
        headers=student_headers,
    )
    assert paid.status_code == 201
    after_paid = client.post(
        "/api/tuition/me/payments",
        json={"idempotencyKey": "pay-again"},
        headers=student_headers,
    )
    assert after_paid.status_code == 409
    assert after_paid.json()["error"] == "INVOICE_ALREADY_PAID"

    student2_user = User(
        username="sv2",
        password_hash=hash_password("Sv2@12345"),
        full_name="Sinh viên thứ hai",
        role=Role.STUDENT,
    )
    db_session.add(student2_user)
    db_session.flush()
    student2 = Student(user_id=student2_user.id, student_code="20210002")
    db_session.add(student2)
    db_session.commit()
    student2_headers = login(client, "sv2", "Sv2@12345")
    foreign_receipt = client.get(f"/api/receipts/{paid.json()['id']}", headers=student2_headers)
    assert foreign_receipt.status_code == 403
    assert (
        client.get(f"/api/receipts/{paid.json()['id']}", headers=lecturer_headers).status_code
        == 403
    )
    assert (
        client.get(f"/api/receipts/{paid.json()['id']}", headers=student_headers).status_code == 200
    )
    assert (
        client.get("/api/admin/tuition/invoices?semesterId=1", headers=lecturer_headers).status_code
        == 403
    )
    assert (
        client.get(
            f"/api/admin/tuition/invoices?semesterId={world['semester'].id}",
            headers=admin_headers,
        ).status_code
        == 200
    )


def test_admin_tuition_configuration_generation_and_reporting(client, db_session):
    world = _tuition_world(db_session)
    admin_headers = login(client, "admin", "Admin@123")

    rates = client.get(
        f"/api/admin/tuition-rates?semesterId={world['semester'].id}",
        headers=admin_headers,
    )
    assert rates.status_code == 200
    assert rates.json()["items"][0]["effectiveFrom"] == "2026-09-07"

    duplicate_rate = client.post(
        "/api/admin/tuition-rates",
        headers=admin_headers,
        json={
            "semesterId": world["semester"].id,
            "cohort": "K66",
            "major": "CNTT",
            "pricePerCredit": 12000,
        },
    )
    assert duplicate_rate.status_code == 409
    assert duplicate_rate.json()["error"] == "DUPLICATE_CODE"

    generated = client.post(
        "/api/admin/tuition/invoices/generate",
        headers=admin_headers,
        json={"semesterId": world["semester"].id, "studentId": world["student"].id},
    )
    assert generated.status_code == 200, generated.text
    assert generated.json()["totalGenerated"] == 1

    invoices = client.get(
        f"/api/admin/tuition/invoices?semesterId={world['semester'].id}&page=1&size=10",
        headers=admin_headers,
    )
    assert invoices.status_code == 200
    assert invoices.json()["items"][0]["amountDue"] == 15000
    summary = client.get(
        f"/api/admin/tuition/reports/summary?semesterId={world['semester'].id}",
        headers=admin_headers,
    )
    assert summary.status_code == 200
    assert summary.json()["totalInvoices"] == 1
    assert summary.json()["totalAmountDue"] == 15000


def test_student_tuition_rejects_unknown_semester(client):
    student_headers = login(client, "sv1", "Sv@12345")
    response = client.get("/api/tuition/me?semesterId=999999", headers=student_headers)
    assert response.status_code == 404


def test_student_tuition_requires_a_rate_when_registered(client, db_session):
    world = _tuition_world(db_session)
    db_session.delete(world["rate"])
    db_session.commit()

    student_headers = login(client, "sv1", "Sv@12345")
    response = client.get(
        f"/api/tuition/me?semesterId={world['semester'].id}", headers=student_headers
    )
    assert response.status_code == 404
    assert response.json()["error"] == "TUITION_RATE_NOT_FOUND"
