from tests.conftest import login


def test_login_success_returns_camel_case_and_no_password(client):
    res = client.post("/api/auth/login", json={"username": "sv1", "password": "Sv@12345"})
    assert res.status_code == 200
    body = res.json()
    assert body["tokenType"] == "Bearer"
    assert body["expiresIn"] == 3600
    assert body["user"]["role"] == "STUDENT"
    assert body["user"]["studentCode"] == "20210001"
    assert body["user"]["lecturerCode"] is None  # trường luôn có mặt, null khi không áp dụng
    assert "password" not in str(body).lower()


def test_login_wrong_password(client):
    res = client.post("/api/auth/login", json={"username": "sv1", "password": "sai"})
    assert res.status_code == 401
    assert res.json()["error"] == "INVALID_CREDENTIALS"


def test_login_locked_account(client):
    res = client.post("/api/auth/login", json={"username": "locked", "password": "Locked@123"})
    assert res.status_code == 403
    assert res.json()["error"] == "ACCOUNT_LOCKED"


def test_login_validation_error_has_field_details(client):
    res = client.post("/api/auth/login", json={})
    assert res.status_code == 400
    body = res.json()
    assert body["error"] == "VALIDATION_ERROR"
    assert {d["field"] for d in body["details"]} == {"username", "password"}
    assert body["timestamp"].endswith("+07:00")


def test_me_requires_token(client):
    res = client.get("/api/auth/me")
    assert res.status_code == 401
    assert res.json()["error"] == "UNAUTHORIZED"


def test_me_with_token(client):
    res = client.get("/api/auth/me", headers=login(client, "gv1", "Gv@12345"))
    assert res.status_code == 200
    assert res.json()["lecturerCode"] == "GV001"


def test_garbage_token_is_unauthorized(client):
    res = client.get("/api/auth/me", headers={"Authorization": "Bearer abc.def.ghi"})
    assert res.status_code == 401
    assert res.json()["error"] == "UNAUTHORIZED"
