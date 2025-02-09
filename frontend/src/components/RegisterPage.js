import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import axios from "axios";
import "../App.css";
import { toast, ToastContainer } from "react-toastify";
import "react-toastify/dist/ReactToastify.css";

const API_URL = "http://127.0.0.1:5000/auth/register";  // ✅ Исправленный путь

const RegisterPage = () => {
    const [username, setUsername] = useState("");
    const [password, setPassword] = useState("");
    const [error, setError] = useState(null);
    const navigate = useNavigate();

    const handleRegister = async (e) => {
        e.preventDefault();
        if (!username || !password) {
            setError("⚠️ Введите имя пользователя и пароль");
            return;
        }

        try {
            await axios.post(API_URL, { username, password }, {
                headers: { "Content-Type": "application/json" },
                withCredentials: true  // ✅ Передача токенов/куков при CORS
            });

            setError(null); // ✅ Очищаем предыдущие ошибки
            
            // ✅ Логируем, чтобы убедиться, что код выполняется
            console.log("✅ Регистрация успешна! Пытаемся показать уведомление...");
            
toast.success("Регистрация успешна! Теперь войдите.", {
    position: "top-right",
    autoClose: 3000,
    hideProgressBar: false,
    closeOnClick: true,
    pauseOnHover: true,
    draggable: true,
    closeButton: false,  // ❌ Убираем крестик
    style: { fontSize: "16px" } // 🖋 Увеличиваем текст, если нужно
});


            // ✅ Перенаправляем через 3 секунды после уведомления
            setTimeout(() => navigate("/"), 3000);
        } catch (error) {
            setError(error.response?.data?.error || "Ошибка регистрации");
        }
    };

    return (
        <div className="auth-container">
            <div className="auth-box">
                <h2>Регистрация</h2>
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
                <button onClick={handleRegister}>ЗАРЕГИСТРИРОВАТЬСЯ</button>
                <a href="/" className="register-link">Уже есть аккаунт? Войти</a>
            </div>

            {/* 🔥 Обязательно добавляем ToastContainer для уведомлений */}
            <ToastContainer />
        </div>
    );
};

export default RegisterPage;
