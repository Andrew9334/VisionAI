from flask import Blueprint, request, jsonify
from flask_cors import CORS
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from werkzeug.security import generate_password_hash, check_password_hash

# 📌 Создаём Blueprint (модуль) для авторизации
auth_bp = Blueprint("auth", __name__)
CORS(auth_bp, resources={r"/*": {"origins": "http://localhost:3000"}}, supports_credentials=True)

# 📌 Фейковая база пользователей (данные хранятся в оперативной памяти)
fake_users = {}

# 📌 Регистрация нового пользователя
@auth_bp.route("/register", methods=["POST"])
def register():
    data = request.json
    username = data.get("username")
    password = data.get("password")

    if not username or not password:
        return jsonify({"error": "Имя пользователя и пароль обязательны"}), 400

    if username in fake_users:
        return jsonify({"error": "Пользователь уже существует"}), 400

    fake_users[username] = generate_password_hash(password)  # Храним хеш пароля
    return jsonify({"message": "Пользователь зарегистрирован!"}), 201

# 📌 Вход пользователя (авторизация)
@auth_bp.route("/login", methods=["POST"])
def login():
    data = request.json
    username = data.get("username")
    password = data.get("password")

    if username not in fake_users or not check_password_hash(fake_users[username], password):
        return jsonify({"error": "Неверные учетные данные"}), 401

    access_token = create_access_token(identity=username)
    return jsonify({"token": access_token, "message": "Успешный вход"}), 200

# 📌 Защищённый маршрут (нужен токен)
@auth_bp.route("/protected", methods=["GET"])
@jwt_required()
def protected():
    username = get_jwt_identity()
    return jsonify({"message": f"Привет, {username}! Это защищённый API."})
