FROM nginx:1.31-alpine

# tzdata: để $time_iso8601 ra +07:00 đúng quy ước ngày giờ của API
RUN apk add --no-cache tzdata
ENV TZ=Asia/Ho_Chi_Minh

# Mọi file *.template được entrypoint của image chạy envsubst rồi ghi vào /etc/nginx/conf.d/
COPY templates/ /etc/nginx/templates/
COPY proxy_api.inc /etc/nginx/conf.d/proxy_api.inc

# Giá trị mặc định (ghi đè bằng biến môi trường / docker-compose)
ENV BACKEND_URL=http://backend:8000 \
    FRONTEND_URL=http://frontend:80 \
    DNS_RESOLVER=127.0.0.11 \
    API_RATE=30r/s \
    LOGIN_RATE=30r/m

EXPOSE 80
HEALTHCHECK --interval=15s --timeout=3s --retries=5 \
  CMD wget -qO- http://127.0.0.1/health || exit 1
