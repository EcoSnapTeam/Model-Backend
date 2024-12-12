# Gunakan image dasar yang sudah ada, berbasis Python 3.10
FROM python:3.10-slim

# Set working directory
WORKDIR /app

# Menyalin requirements.txt ke dalam image
COPY requirements.txt .

# Install dependensi yang ada di requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Menyalin seluruh kode aplikasi ke dalam image
COPY . .

# Set environment variable untuk Flask
ENV FLASK_APP=app.py
ENV FLASK_RUN_HOST=0.0.0.0

# Port yang akan digunakan
EXPOSE 8080

# Menjalankan aplikasi Flask
CMD ["flask", "run"]
