"""Kiểm tra lớp phân quyền thứ nhất (Security Filter) — chạy được ngay cả khi Service còn là khung."""

from tests.conftest import login


def test_student_cannot_call_admin_endpoint(client):
    res = client.get("/api/subjects", headers=login(client, "sv1", "Sv@12345"))
    assert res.status_code == 403
    assert res.json()["error"] == "FORBIDDEN"


def test_lecturer_cannot_register(client):
    res = client.post(
        "/api/registrations", json={"sectionId": 1}, headers=login(client, "gv1", "Gv@12345")
    )
    assert res.status_code == 403


def test_admin_passes_filter_and_hits_unimplemented_service(client):
    res = client.get("/api/subjects", headers=login(client, "admin", "Admin@123"))
    assert res.status_code == 501  # qua được filter; Service chưa triển khai
    assert res.json()["error"] == "NOT_IMPLEMENTED"


def test_section_payload_validation_points_at_field(client):
    payload = {
        "sectionCode": "150001",
        "subjectId": 1,
        "semesterId": 1,
        "lecturerId": 1,
        "roomId": 1,
        "dayOfWeek": 3,
        "startPeriod": 5,
        "endPeriod": 3,
        "startWeek": 1,
        "endWeek": 15,
        "maxCapacity": 0,
    }
    res = client.post("/api/sections", json=payload, headers=login(client, "admin", "Admin@123"))
    assert res.status_code == 400
    fields = {d["field"] for d in res.json()["details"]}
    assert {"endPeriod", "maxCapacity"} <= fields
