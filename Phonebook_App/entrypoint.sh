#!/bin/sh
# entrypoint.sh — Đợi MySQL sẵn sàng trước khi khởi động app

set -e

HOST="${MYSQL_HOST:-db}"
PORT="${MYSQL_PORT:-3306}"

echo "⏳ Đang chờ MySQL tại ${HOST}:${PORT} ..."

# Thử kết nối mỗi 2 giây, tối đa 60 lần (~2 phút)
MAX_TRIES=60
COUNT=0
until nc -z "$HOST" "$PORT"; do
    COUNT=$((COUNT + 1))
    if [ "$COUNT" -ge "$MAX_TRIES" ]; then
        echo "❌ Không thể kết nối MySQL sau ${MAX_TRIES} lần thử. Thoát."
        exit 1
    fi
    echo "   ... chờ (${COUNT}/${MAX_TRIES})"
    sleep 2
done

echo "✅ MySQL đã sẵn sàng! Đang khởi động ứng dụng..."

# Thực thi lệnh được truyền vào (CMD)
exec "$@"
