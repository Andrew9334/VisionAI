import sys
import os
import numpy as np
from flask_cors import CORS
from flask import Flask, request, jsonify
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from werkzeug.security import generate_password_hash, check_password_hash

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
PROJECT_DIR = os.path.abspath(os.path.join(BASE_DIR, ".."))
SERVICES_DIR = os.path.join(PROJECT_DIR, "services")

sys.path.append(SERVICES_DIR)

from tf_predict import predict_single_image  
from clip_predict import CLIPpredictor       
from yolo_predict import predict_image       

try:
    from resnet_predict import predict_car_image
    CAR_MODEL_AVAILABLE = True
except ImportError:
    CAR_MODEL_AVAILABLE = False

app = Flask(__name__)
app.config["JWT_SECRET_KEY"] = "supersecretkey"
CORS(app, resources={r"/*": {"origins": "http://localhost:3000"}}, supports_credentials=True)
jwt = JWTManager(app)

UPLOAD_FOLDER = os.path.join(BASE_DIR, "uploads")
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

clip_model = CLIPpredictor()

INCOME_MAPPING = {
    "low_income": "Бедный",
    "middle_income": "Средний",
    "high_income": "Богатый"
}

EQUIPMENT_MAPPING = {
    "cheap equipment": "Дешевое оборудование",
    "medium-price equipment": "Среднеценовое оборудование",
    "expensive equipment": "Дорогое оборудование",
    "luxury equipment": "Роскошное оборудование",
    "old equipment": "Старое оборудование",
    "modern equipment": "Современное оборудование",
    "broken equipment": "Сломанное оборудование",
    "high-tech equipment": "Высокотехнологичное оборудование",
    "standard equipment": "Стандартное оборудование"
}

INCOME_SCORES = {
    "Бедный": 1,
    "Средний": 2,
    "Богатый": 3
}

def map_income_class(class_name, mapping):
    """Преобразует предсказание модели в нормальное значение"""
    return mapping.get(class_name.lower(), "Неизвестно") if class_name else "Неизвестно"

def calculate_overall_class(predictions):
    """Рассчитывает общий класс на основе всех предсказаний"""
    scores = [INCOME_SCORES.get(pred["class"], 2) for pred in predictions]
    confidences = [pred["confidence"] for pred in predictions if "confidence" in pred and pred["confidence"] > 0]

    if not scores:
        return "Неизвестно", 0.0

    avg_score = round(sum(scores) / len(scores))
    avg_confidence = sum(confidences) / len(confidences) if confidences else 0.0

    overall_class = {1: "Бедный", 2: "Средний", 3: "Богатый"}.get(avg_score, "Неизвестно")
    
    return overall_class, round(avg_confidence, 4)

def process_real_estate(file_path):
    """Обрабатывает изображение недвижимости (YOLO + TensorFlow)"""
    yolo_class, yolo_conf, _ = predict_image(file_path)
    tf_class, tf_conf, _ = predict_single_image(file_path)

    return {
        "yolo": {
            "model": "YOLO",
            "class": map_income_class(yolo_class, INCOME_MAPPING),
            "confidence": round(float(yolo_conf), 4) if yolo_conf else 0.0
        },
        "tensorflow": {
            "model": "TensorFlow",
            "class": map_income_class(tf_class, INCOME_MAPPING),
            "confidence": round(float(tf_conf), 4) if tf_conf else 0.0
        }
    }

def process_tech(file_path):
    """Обрабатывает изображение техники (CLIP)"""
    clip_result = clip_model.predict(file_path)

    predicted_class = clip_result.get("class", "").lower()
    mapped_class = EQUIPMENT_MAPPING.get(predicted_class, predicted_class)  # Если нет в маппинге, используем оригинальное название

    if predicted_class not in EQUIPMENT_MAPPING:
        print(f"⚠️ Неизвестный класс от CLIP: {predicted_class}. Добавьте его в EQUIPMENT_MAPPING!")

    return {
        "clip": {
            "model": "CLIP",
            "class": mapped_class if mapped_class else "Неизвестно",
            "confidence": round(float(clip_result.get("confidence", 0.0)), 4)
        }
    }

def process_cars(file_path):
    """Обрабатывает изображение автомобиля (ResNet)"""
    if not CAR_MODEL_AVAILABLE:
        return {"error": "Модель для автомобилей не доступна"}

    car_class, car_conf, _ = predict_car_image(file_path)

    return {
        "resnet": {
            "model": "ResNet",
            "class": map_income_class(car_class, INCOME_MAPPING),
            "confidence": round(float(car_conf), 4) if car_conf else 0.0
        }
    }

@app.before_request
def handle_options():
    """Обрабатывает preflight-запросы (OPTIONS)"""
    if request.method == "OPTIONS":
        response = jsonify({"message": "CORS preflight response"})
        response.headers.add("Access-Control-Allow-Origin", "http://localhost:3000")
        response.headers.add("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        response.headers.add("Access-Control-Allow-Headers", "Content-Type, Authorization")
        response.headers.add("Access-Control-Allow-Credentials", "true")
        return response, 200

@app.route('/predict/', methods=['POST'])
def predict():
    print("🔹 Получен запрос на /predict/")
    
    if 'files' not in request.files:
        return jsonify({"error": "Файлы обязательны"}), 400

    files = request.files.getlist('files')
    types = request.form.getlist('types')

    print("📂 Файлы:", [file.filename for file in files])
    print("🛠 Типы данных:", types)

    if len(files) != len(types):
        return jsonify({"error": "Количество файлов и типов не совпадает"}), 400

    results = {}
    predictions = []

    for file, img_type in zip(files, types):
        file_path = os.path.join(UPLOAD_FOLDER, file.filename)
        file.save(file_path)

        if img_type == "real_estate":
            results["real_estate"] = process_real_estate(file_path)
            predictions.append(results["real_estate"]["tensorflow"])
        elif img_type == "tech":
            results["tech"] = process_tech(file_path)
            predictions.append(results["tech"]["clip"])
        elif img_type == "car" and CAR_MODEL_AVAILABLE:
            results["car"] = process_cars(file_path)
            predictions.append(results["car"]["resnet"])

    overall_class, overall_confidence = calculate_overall_class(predictions)

    response = {
        "files": [file.filename for file in files],
        "final_class": overall_class,
        "final_confidence": overall_confidence,
        "results": results
    }

    print("✅ Ответ API:", response)
    return jsonify(response)

from auth import auth_bp  # Импортируем Blueprint из auth.py
app.register_blueprint(auth_bp, url_prefix="/auth")  # Регистрируем Blueprint с префиксом /auth

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000, debug=True)
