from flask import Blueprint, request, jsonify
from flask_cors import CORS
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy.orm import Session
from db import get_db  # 🔹 Подключение к БД
from models import User  # 🔹 Импортируем модель пользователя

# 📌 Создаём Blueprint (модуль) для авторизации
auth_bp = Blueprint("auth", __name__)
CORS(auth_bp, resources={r"/*": {"origins": "http://localhost:3000"}}, supports_credentials=True)

# 📌 Регистрация нового пользователя
@auth_bp.route("/register", methods=["POST"])
def register():
    data = request.json
    username = data.get("username")
    password = data.get("password")

    if not username or not password:
        return jsonify({"error": "Имя пользователя и пароль обязательны"}), 400

    db: Session = next(get_db())

    # Проверяем, существует ли пользователь
    existing_user = db.query(User).filter(User.username == username).first()
    if existing_user:
        return jsonify({"error": "Пользователь уже существует"}), 400

    # Создаём нового пользователя и хешируем пароль
    new_user = User(username=username, password_hash=generate_password_hash(password))
    db.add(new_user)
    db.commit()  # 💾 Сохраняем пользователя в БД!
    
    return jsonify({"message": "Пользователь зарегистрирован!"}), 201

# 📌 Вход пользователя (авторизация)
@auth_bp.route("/login", methods=["POST"])
def login():
    data = request.json
    username = data.get("username")
    password = data.get("password")

    db: Session = next(get_db())
    user = db.query(User).filter(User.username == username).first()

    if not user or not check_password_hash(user.password_hash, password):
        return jsonify({"error": "Неверные учетные данные"}), 401

    access_token = create_access_token(identity=username)
    return jsonify({"token": access_token, "message": "Успешный вход"}), 200

# 📌 Защищённый маршрут (нужен токен)
@auth_bp.route("/protected", methods=["GET"])
@jwt_required()
def protected():
    username = get_jwt_identity()
    return jsonify({"message": f"Привет, {username}! Это защищённый API."})
