# Menggunakan image Python 3.9 sebagai base image
FROM python:3.9-slim

# Set working directory di dalam container
WORKDIR /app

# Menyalin requirements.txt ke dalam container
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Menyalin seluruh file aplikasi ke dalam container
COPY . .

# Salin file key.json ke dalam container
COPY key.json /app/key.json

# Set variabel lingkungan untuk Google Application Credentials
ENV GOOGLE_APPLICATION_CREDENTIALS="/app/key.json"

# Expose port 8080 (default untuk Cloud Run)
EXPOSE 8080

# Menjalankan aplikasi Flask menggunakan Gunicorn
CMD ["gunicorn", "-b", "0.0.0.0:8080", "app:app"]
