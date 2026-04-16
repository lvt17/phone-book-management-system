# ─────────────────────────────────────────────────────────────
# Stage: Runtime image cho Phonebook CLI
# ─────────────────────────────────────────────────────────────
FROM python:3.11-slim

# 1. Thiết lập thư mục làm việc trong container
WORKDIR /app

# 2. Cài đặt thư viện hệ thống cần thiết
#    - gcc / python3-dev: để build mysql-connector-python
#    - netcat-openbsd  : dùng trong entrypoint để chờ MySQL sẵn sàng
RUN apt-get update && apt-get install -y \
    gcc \
    python3-dev \
    netcat-openbsd \
    && rm -rf /var/lib/apt/lists/*

# 3. Copy & cài thư viện Python trước (tận dụng Docker layer cache)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 4. Copy toàn bộ source code vào container
COPY . .

# 5. Cấp quyền thực thi cho entrypoint script
RUN chmod +x /app/entrypoint.sh

# 6. Biến môi trường mặc định (có thể override khi chạy container)
ENV MYSQL_HOST=db
ENV MYSQL_PORT=3306
ENV MYSQL_USER=root
ENV MYSQL_PASSWORD=rootpassword
ENV MYSQL_DATABASE=phonebook

# 7. Chạy qua entrypoint để đợi MySQL trước, sau đó mới chạy app
ENTRYPOINT ["/app/entrypoint.sh"]
CMD ["python", "-u", "main.py"]
