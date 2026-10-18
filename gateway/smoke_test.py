"""Kiểm tra nhanh gateway (chỉ dùng thư viện chuẩn, chạy được trên Windows / CI).

    python smoke_test.py                       # mặc định http://localhost:8080
    python smoke_test.py http://localhost:8080 # hoặc truyền địa chỉ gateway
"""

import json
import sys
import urllib.error
import urllib.request

BASE = (sys.argv[1] if len(sys.argv) > 1 else "http://localhost:8080").rstrip("/")
failed = 0


def call(path: str, method: str = "GET", body: dict | None = None):
    data = json.dumps(body).encode() if body is not None else None
    req = urllib.request.Request(BASE + path, data=data, method=method,
                                 headers={"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=5) as res:
            return res.status, dict(res.headers), res.read().decode()
    except urllib.error.HTTPError as err:
        return err.code, dict(err.headers), err.read().decode()


def check(name: str, ok: bool, detail: str = "") -> None:
    global failed
    print(("PASS " if ok else "FAIL ") + name + ("" if ok else f"  -> {detail}"))
    failed += 0 if ok else 1


status, headers, _ = call("/health")
check("gateway /health = 200", status == 200, str(status))
check("có header X-Request-Id", "X-Request-Id" in headers)
check("không lộ phiên bản nginx", "nginx/" not in headers.get("Server", ""), headers.get("Server", ""))

status, _, body = call("/health/backend")
check("backend /health qua gateway = 200", status == 200, f"{status} {body}")

status, _, body = call("/api/auth/me")
payload = json.loads(body) if body.startswith("{") else {}
check("/api/auth/me không token = 401 UNAUTHORIZED (lỗi của backend đi nguyên vẹn)",
      status == 401 and payload.get("error") == "UNAUTHORIZED", f"{status} {body}")

status, _, body = call("/api/auth/login", "POST", {"username": "x", "password": "y"})
payload = json.loads(body) if body.startswith("{") else {}
check("login sai = 401 INVALID_CREDENTIALS",
      status == 401 and payload.get("error") == "INVALID_CREDENTIALS", f"{status} {body}")

sys.exit(1 if failed else 0)
