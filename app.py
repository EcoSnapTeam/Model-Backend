from flask import Flask, request, jsonify
import numpy as np
from PIL import Image
import io
import os
from google.cloud import storage
from keras.models import load_model
from google.cloud import firestore
import requests


app = Flask(__name__)

# Fungsi untuk mengunduh model dari Google Cloud Storage
def download_model(bucket_name, model_file, local_path):
    client = storage.Client()
    bucket = client.bucket(bucket_name)
    blob = bucket.blob(model_file)
    blob.download_to_filename(local_path)
    print(f"Model {model_file} berhasil diunduh ke {local_path}")

# Nama bucket dan path model
BUCKET_NAME = "model-ecosnap"
BUCKET_UPLOADS = "ecosnap"
MODEL_FILE = "model2.h5"  # Gunakan .h5 untuk model Keras

# Tentukan path lokal
LOCAL_MODEL_PATH = "tmp/model.h5"  # Menggunakan direktori lokal

# Mengecek apakah model sudah ada, jika belum unduh modelnya
if not os.path.exists(LOCAL_MODEL_PATH):
    download_model(BUCKET_NAME, MODEL_FILE, LOCAL_MODEL_PATH)

# Memuat model Keras (.h5)
model = load_model(LOCAL_MODEL_PATH)

# Inisialisasi Firestore
db = firestore.Client()

# Fungsi untuk melakukan prediksi
def predict_image(image_bytes):
    image = Image.open(io.BytesIO(image_bytes))
    image = image.resize((128, 128))  # Resize gambar ke 128x128 sesuai dengan input model
    image_array = np.array(image).astype(np.float32)
    image_array = np.expand_dims(image_array, axis=0)
    
    # Lakukan prediksi dengan model Keras
    output = model.predict(image_array)
    
    # Menentukan label dan confidence
    label = np.argmax(output)
    confidence = np.max(output)

    # Nama kelas berdasarkan indeks
    class_names = ["Kaca", "Logam", "Kertas", "Residu", "Kardus", "Plastik"]
    label_name = class_names[label]
    suggestion = get_suggestion(label_name)

    return {
        "label": label_name,
        "confidence": confidence * 100,
        "suggestion": suggestion,
    }

# Fungsi untuk memberikan saran berdasarkan label
def get_suggestion(label_name):
    suggestions = {
        "Kaca": "Pisahkan kaca dari sampah lainnya dan tempatkan di tempat sampah khusus kaca.",
        "Logam": "Pisahkan logam dari sampah lainnya dan tempatkan di tempat sampah khusus logam.",
        "Kertas": "Pisahkan kertas dari sampah lainnya dan tempatkan di tempat sampah khusus kertas.",
        "Residu": "Tempatkan residu di tempat sampah umum.",
        "Kardus": "Pisahkan kardus dari sampah lainnya dan tempatkan di tempat sampah khusus kardus.",
        "Plastik": "Pisahkan plastik dari sampah lainnya dan tempatkan di tempat sampah khusus plastik.",
    }
    return suggestions.get(label_name, "Tidak ada saran untuk jenis sampah ini.")

# Fungsi untuk menyimpan hasil prediksi ke Firestore
def save_predict(prediction):
    try:
        # Koleksi Firestore untuk menyimpan prediksi
        collection_name = "predictions"
        
        # Data yang akan disimpan
        data = {
            "label": prediction["label"],
            "confidence": prediction["confidence"],
            "suggestion": prediction["suggestion"],
            "image_url": prediction.get("image_url", ""),
            "timestamp": firestore.SERVER_TIMESTAMP  # Menambahkan timestamp secara otomatis
        }
        
        # Simpan data ke Firestore
        db.collection(collection_name).add(data)
        print("Hasil prediksi berhasil disimpan ke Firestore")
    except Exception as e:
        print(f"Error menyimpan ke Firestore: {e}")
        
def upload_to_bucket(bucket_name, folder_name, file_name, file_bytes):
    try:
        # Inisialisasi klien Google Cloud Storage
        client = storage.Client()
        bucket = client.bucket(bucket_name)
        
        # Path file di bucket
        blob_name = f"{folder_name}/{file_name}"
        blob = bucket.blob(blob_name)
        
        # Unggah file ke bucket
        blob.upload_from_file(io.BytesIO(file_bytes), content_type="image/jpeg")
        print(f"File {file_name} berhasil diunggah ke {blob_name} di bucket {bucket_name}")
        
        # Buat URL file secara manual
        file_url = f"https://storage.googleapis.com/{bucket_name}/{blob_name}"
        return file_url
    except Exception as e:
        print(f"Error mengunggah ke bucket: {e}")
        return None

# Modifikasi endpoint predict untuk menyimpan hasil prediksi ke Firestore
@app.route("/predict", methods=["POST"])
def predict():
    # Cek apakah request mengandung file atau URL
    file = request.files.get('file')
    url = request.form.get('url')  # Parameter URL untuk file di bucket
    
    if not file and not url:
        return jsonify({"error": "No file or URL provided"}), 400
    
    try:
        # Jika file diunggah, baca file sebagai bytes
        if file:
            image_bytes = file.read()
            file_name = file.filename
        elif url:
            # Unduh file dari URL
            response = requests.get(url)
            if response.status_code != 200:
                return jsonify({"error": "Failed to fetch file from URL"}), 400
            
            image_bytes = response.content
            file_name = url.split("/")[-1]  # Ambil nama file dari URL
        
        # Lakukan prediksi gambar
        prediction = predict_image(image_bytes)
        
        if file:
            # Upload gambar ke Google Cloud Storage
            folder_name = "uploads"
            public_url = upload_to_bucket(BUCKET_UPLOADS, folder_name, file_name, image_bytes)
            
            if public_url:
                prediction["image_url"] = public_url 
        elif url:
            prediction["image_url"] = url
        
        # Simpan hasil prediksi ke Firestore
        save_predict(prediction)
        
        return jsonify(prediction)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Endpoint untuk pengecekan status server
@app.route("/health", methods=["GET"])
def health_check():
    return jsonify({"status": "ok"})

# Endpoint untuk informasi tentang model
@app.route("/info", methods=["GET"])
def model_info():
    return jsonify({
        "model": "Keras (.h5)",
        "description": "Model ini digunakan untuk mengklasifikasikan jenis sampah berdasarkan gambar.",
        "input_size": "224x224 pixels",
        "output_classes": ["Kaca", "Logam", "Kertas", "Residu", "Kardus", "Plastik"]
    })

if __name__ == '__main__':
    app.run(debug=True)
