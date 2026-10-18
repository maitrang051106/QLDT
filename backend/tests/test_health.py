def test_health(client):
    res = client.get("/health")
    assert res.status_code == 200
    assert res.json() == {"status": "ok"}


def test_unknown_route_uses_error_format(client):
    res = client.get("/api/khong-ton-tai")
    assert res.status_code == 404
    body = res.json()
    assert body["error"] == "NOT_FOUND"
    assert body["path"] == "/api/khong-ton-tai"
    assert body["details"] == []
