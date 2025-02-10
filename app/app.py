import os
import requests
from flask_cors import CORS
from flask import Flask, request, jsonify
from flask_jwt_extended import JWTManager

# Загружаем URL сервисов моделей из переменных окружения
YOLO_URL = os.getenv("YOLO_URL", "http://yolo:5001")
TENSORFLOW_URL = os.getenv("TENSORFLOW_URL", "http://tensorflow:5002")
CLIP_URL = os.getenv("CLIP_URL", "http://clip:5003")

app = Flask(__name__)
app.config["JWT_SECRET_KEY"] = os.getenv("JWT_SECRET_KEY", "supersecretkey")
CORS(app, resources={r"/*": {"origins": "http://localhost:3000"}}, supports_credentials=True)
jwt = JWTManager(app)

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def send_request(url, file_path):
    """Отправляет файл на указанный URL сервиса модели"""
    with open(file_path, "rb") as file:
        response = requests.post(url, files={"file": file})
        return response.json() if response.status_code == 200 else {"error": f"Ошибка запроса к {url}"}

def process_real_estate(file_path):
    """Запрашивает предсказания у YOLO и TensorFlow"""
    yolo_response = send_request(f"{YOLO_URL}/predict", file_path)
    tf_response = send_request(f"{TENSORFLOW_URL}/predict", file_path)

    return {"yolo": yolo_response, "tensorflow": tf_response}

def process_tech(file_path):
    """Запрашивает предсказания у CLIP"""
    return {"clip": send_request(f"{CLIP_URL}/predict", file_path)}

@app.route('/predict/', methods=['POST'])
def predict():
    if 'files' not in request.files:
        return jsonify({"error": "Файлы обязательны"}), 400

    files = request.files.getlist('files')
    types = request.form.getlist('types')

    if len(files) != len(types):
        return jsonify({"error": "Количество файлов и типов не совпадает"}), 400

    results = {}
    for file, img_type in zip(files, types):
        file_path = os.path.join(UPLOAD_FOLDER, file.filename)
        file.save(file_path)

        if img_type == "real_estate":
            results["real_estate"] = process_real_estate(file_path)
        elif img_type == "tech":
            results["tech"] = process_tech(file_path)

    return jsonify({"results": results})

from auth import auth_bp
app.register_blueprint(auth_bp, url_prefix="/auth")

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000, debug=True)
