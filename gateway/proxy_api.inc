proxy_pass $backend_upstream;
proxy_http_version 1.1;

# Backend cần biết client thật và đường đi ban đầu (log, và dựng URL tuyệt đối nếu có)
proxy_set_header Host $host;
proxy_set_header X-Real-IP $remote_addr;
proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
proxy_set_header X-Forwarded-Proto $scheme;
proxy_set_header X-Request-Id $request_id;
proxy_set_header Connection "";

proxy_connect_timeout 3s;
proxy_send_timeout 15s;
proxy_read_timeout 30s;

# Đừng chuyển lỗi của backend thành trang lỗi của gateway: để ErrorResponse của backend đi nguyên vẹn
proxy_intercept_errors off;
# Không retry các request ghi sang upstream khác (tránh đăng ký hai lần)
proxy_next_upstream off;
