import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import axios from "axios";
import "../App.css";

const API_URL = "http://127.0.0.1:5000/auth/login";  // ✅ Исправленный путь

const LoginPage = ({ setToken }) => {
    const [username, setUsername] = useState("");
    const [password, setPassword] = useState("");
    const [error, setError] = useState(null);
    const navigate = useNavigate();

    const handleLogin = async (e) => {
        e.preventDefault();
        if (!username || !password) {
            setError("⚠️ Введите имя пользователя и пароль");
            return;
        }

        try {
            const response = await axios.post(API_URL, { username, password }, {
                headers: {
                    "Content-Type": "application/json"
                },
                withCredentials: true  // ✅ Позволяет передавать куки/токены при CORS
            });

            const token = response.data.token;
            localStorage.setItem("token", token);  // ✅ Сохраняем токен
            setToken(token);
            navigate("/app");  // ✅ Перенаправляем после входа
        } catch (error) {
            setError(error.response?.data?.error || "Ошибка входа");
        }
    };

    return (
        <div className="auth-container">
            <div className="auth-box">
                <h2>Вход</h2>
                {error && <p className="error-message">{error}</p>}
                <input
                    type="text"
                    placeholder="Имя пользователя"
                    className="input-field"
                    value={username}
                    onChange={(e) => setUsername(e.target.value)}
                />
                <input
                    type="password"
                    placeholder="Пароль"
                    className="input-field"
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                />
                <button onClick={handleLogin}>ВОЙТИ</button>
                <a href="/register" className="register-link">Нет аккаунта? Зарегистрироваться</a>
            </div>
        </div>
    );
};

export default LoginPage;
