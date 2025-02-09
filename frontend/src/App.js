import { BrowserRouter as Router, Routes, Route, Navigate } from "react-router-dom";
import LoginPage from "./components/LoginPage";
import UploadForm from "./components/UploadForm";
import RegisterPage from "./components/RegisterPage";
import { useState, useEffect } from "react";

const App = () => {
    const [token, setToken] = useState(null); // Начинаем с null

    useEffect(() => {
        const storedToken = localStorage.getItem("token");
        console.log("Токен в localStorage:", storedToken);
        setToken(storedToken); // Явно обновляем состояние
    }, []);

    return (
        <Router>
            <Routes>
                <Route path="/" element={!token ? <LoginPage setToken={setToken} /> : <Navigate to="/app" />} />
                <Route path="/register" element={<RegisterPage />} />
                <Route path="/app" element={token ? <UploadForm /> : <Navigate to="/" />} />
            </Routes>
        </Router>
    );
};

export default App;
