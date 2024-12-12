from flask import Flask, request, jsonify
import numpy as np
from PIL import Image
import io
import os
from google.cloud import storage
from keras.models import load_model

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
MODEL_FILE = "model2.h5"  # Gunakan .h5 untuk model Keras

# Tentukan path lokal
LOCAL_MODEL_PATH = "/tmp/model.h5"  # Menggunakan direktori lokal

# Mengecek apakah model sudah ada, jika belum unduh modelnya
if not os.path.exists(LOCAL_MODEL_PATH):
    download_model(BUCKET_NAME, MODEL_FILE, LOCAL_MODEL_PATH)

# Memuat model Keras (.h5)
model = load_model(LOCAL_MODEL_PATH)

# Fungsi untuk melakukan prediksi
def predict_image(image_bytes):
    image = Image.open(io.BytesIO(image_bytes))
    image = image.resize((128, 128))  # Resize gambar ke input model
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
        "confidence": float(confidence * 100),  # Konversi ke float Python
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

# Endpoint untuk menerima file gambar dan memberikan prediksi
@app.route("/predict", methods=["POST"])
def predict():
    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400
    
    try:
        image_bytes = file.read()
        prediction = predict_image(image_bytes)
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
    app.run(host='0.0.0.0', port=8080)
