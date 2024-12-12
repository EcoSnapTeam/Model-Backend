# Backend Model API - EcoSnap

## Deskripsi Proyek
Backend ini dirancang untuk melayani aplikasi **EcoSnap**, sebuah platform yang menggunakan model machine learning untuk mengklasifikasikan jenis sampah dari gambar yang diunggah. Aplikasi ini bertujuan untuk mendukung pengelolaan sampah yang lebih baik dengan memberikan prediksi jenis sampah dan saran pengelolaannya. Backend ini juga terintegrasi dengan Google Cloud Services untuk penyimpanan gambar dan pencatatan hasil prediksi.

---

## Fitur Utama
1. **Prediksi Jenis Sampah**:
   - Model machine learning (Keras `.h5`) untuk mengklasifikasikan jenis sampah berdasarkan gambar.
   - Jenis sampah yang didukung: `Kaca`, `Logam`, `Kertas`, `Residu`, `Kardus`, `Plastik`.

2. **Penyimpanan Gambar**:
   - Gambar yang diunggah akan disimpan di bucket Google Cloud Storage pada folder `uploads`.

3. **Pencatatan Prediksi**:
   - Hasil prediksi disimpan di Google Firestore dengan rincian label, confidence, saran, dan timestamp.

4. **Integrasi Cloud**:
   - Menggunakan kredensial Google Cloud (key.json) untuk mengakses layanan seperti Firestore dan Cloud Storage.

---

## Struktur Endpoint

### 1. **Prediksi Sampah**  
**Endpoint**: `/predict`  
**Method**: `POST`  
**Deskripsi**: Endpoint ini menerima gambar dalam bentuk file atau URL dari bucket untuk melakukan prediksi.

#### **Request (File)**
```json
POST /predict
Content-Type: multipart/form-data

{
  "file": [Gambar dalam format JPEG/PNG]
}
```

#### **Response**
```json
{
  "label": "Plastik",
  "confidence": 92.5,
  "suggestion": "Pisahkan plastik dari sampah lainnya dan tempatkan di tempat sampah khusus plastik.",
  "image_url": "https://storage.googleapis.com/ecosnap/uploads/plastik.jpg"
}
```

### 2. **Cek Kesehatan Server**  
**Endpoint**: `/health`  
**Method**: `GET`  
**Deskripsi**: Mengembalikan status server.

#### **Response**
```json
{
  "status": "ok"
}
```

### 3. **Informasi Model**  
**Endpoint**: `/info`  
**Method**: `GET`  
**Deskripsi**: Mengembalikan informasi tentang model yang digunakan.

#### **Response**
```json
{
  "model": "Keras (.h5)",
  "description": "Model ini digunakan untuk mengklasifikasikan jenis sampah berdasarkan gambar.",
  "input_size": "128x128 pixels",
  "output_classes": ["Kaca", "Logam", "Kertas", "Residu", "Kardus", "Plastik"]
}
```

---

## Konfigurasi dan Setup

### **1. Persyaratan Sistem**
- Python 3.9 atau lebih baru
- Google Cloud SDK diinstal dan dikonfigurasi
- File kredensial `key.json` dari Google Cloud Platform

### **2. Instalasi Lokal**

#### **Langkah 1: Clone Repository**
```bash
git clone <repository-url>
cd <repository-folder>
```

#### **Langkah 2: Buat Virtual Environment**
```bash
python -m venv venv
source venv/bin/activate  # Untuk Linux/MacOS
venv\Scripts\activate   # Untuk Windows
```

#### **Langkah 3: Instal Dependensi**
```bash
pip install -r requirements.txt
```

#### **Langkah 4: Jalankan Server**
```bash
python app.py
```

Server akan berjalan di `http://127.0.0.1:8080`.

---

## Deployment dengan Docker

### **1. Build Docker Image**
```bash
docker build -t ecosnap-backend .
```

### **2. Jalankan Docker Container**
```bash
docker run -p 8080:8080 ecosnap-backend
```

---

## Variabel Lingkungan

- **`GOOGLE_APPLICATION_CREDENTIALS`**: Path ke file `key.json` untuk mengakses layanan Google Cloud.

---

## Teknologi yang Digunakan
- **Flask**: Framework web untuk membangun API.
- **Gunicorn**: Server WSGI untuk menjalankan aplikasi Flask.
- **Google Cloud Storage**: Untuk menyimpan gambar hasil unggahan.
- **Google Firestore**: Untuk menyimpan hasil prediksi.
- **Keras**: Untuk menjalankan model machine learning.
- **Docker**: Untuk containerisasi aplikasi.

---

## Catatan Tambahan
- Pastikan file `key.json` disimpan dengan aman dan tidak diunggah ke repositori publik.
- Gunakan mekanisme pengelolaan rahasia seperti **Google Secret Manager** untuk deployment ke lingkungan produksi.

