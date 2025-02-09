import { useState } from "react";
import { useNavigate } from "react-router-dom";
import axios from "axios";
import { Button, Typography, Box, Card, CardContent, Grid, Switch, FormControlLabel } from "@mui/material";
import "../App.css"; // Подключаем стили

const API_URL = "http://127.0.0.1:5000";

const UploadForm = () => {
    const [enableRealEstate, setEnableRealEstate] = useState(true);
    const [enableTech, setEnableTech] = useState(true);
    const [enableCar, setEnableCar] = useState(true);

    const [realEstateFile, setRealEstateFile] = useState(null);
    const [techFile, setTechFile] = useState(null);
    const [carFile, setCarFile] = useState(null);

    const [loading, setLoading] = useState(false);
    const [finalResult, setFinalResult] = useState(null);

    const navigate = useNavigate();

    const handleLogout = () => {
        localStorage.removeItem("token");
        window.location.href = "/";
    };

    const handleFileChange = (event, type) => {
        if (type === "real_estate") setRealEstateFile(event.target.files[0]);
        if (type === "tech") setTechFile(event.target.files[0]);
        if (type === "car") setCarFile(event.target.files[0]);
    };

    const handleUpload = async () => {
        const formData = new FormData();
        if (enableRealEstate && realEstateFile) {
            formData.append("files", realEstateFile);
            formData.append("types", "real_estate");
        }
        if (enableTech && techFile) {
            formData.append("files", techFile);
            formData.append("types", "tech");
        }
        if (enableCar && carFile) {
            formData.append("files", carFile);
            formData.append("types", "car");
        }

        setLoading(true);
        try {
            const response = await axios.post(`${API_URL}/predict/`, formData, {
                headers: { "Content-Type": "multipart/form-data" }
            });
            setFinalResult(response.data);
        } catch (error) {
            console.error("Ошибка при отправке:", error);
        }
        setLoading(false);
    };

    return (
        <div className="container" style={{ width: "100%", maxWidth: "600px", padding: "20px", margin: "20px auto" }}>
            
            {/* 🔹 Кнопка "Выйти" */}
            <Box position="absolute" top={10} left={10}>
                <Button variant="contained" color="secondary" onClick={handleLogout}>
                    ВЫЙТИ
                </Button>
            </Box>

            {/* 🔹 Форма загрузки */}
            <Box className="upload-box" sx={{ display: "flex", flexDirection: "column", padding: "20px" }}>
                <Typography variant="h5">Загрузка изображений</Typography>

                <FormControlLabel
                    control={<Switch checked={enableRealEstate} onChange={() => setEnableRealEstate(!enableRealEstate)} color="primary" />}
                    label="Обрабатывать недвижимость"
                />
                {enableRealEstate && (
                    <>
                        <Typography>🏡 Недвижимость:</Typography>
                        <input type="file" onChange={(e) => handleFileChange(e, "real_estate")} />
                    </>
                )}

                <FormControlLabel
                    control={<Switch checked={enableTech} onChange={() => setEnableTech(!enableTech)} color="primary" />}
                    label="Обрабатывать технику"
                />
                {enableTech && (
                    <>
                        <Typography>📱 Техника:</Typography>
                        <input type="file" onChange={(e) => handleFileChange(e, "tech")} />
                    </>
                )}

                <FormControlLabel
                    control={<Switch checked={enableCar} onChange={() => setEnableCar(!enableCar)} color="primary" />}
                    label="Обрабатывать автомобили"
                />
                {enableCar && (
                    <>
                        <Typography>🚗 Автомобиль:</Typography>
                        <input type="file" onChange={(e) => handleFileChange(e, "car")} />
                    </>
                )}

                {/* 🔹 Фиксированная кнопка "Рассчитать" */}
                <Box sx={{ marginTop: "20px", textAlign: "center" }}>
                    <Button variant="contained" color="primary" onClick={handleUpload} disabled={loading}>
                        {loading ? "Рассчитываем..." : "Рассчитать"}
                    </Button>
                </Box>

                {/* 🔹 Контейнер с результатами */}
                {finalResult && (
                    <Box sx={{ marginTop: "20px" }}>
                        <Grid container spacing={2}>
                            {enableRealEstate && finalResult.results.real_estate && (
                                <Grid item xs={12}>
                                    <Card>
                                        <CardContent>
                                            <Typography variant="h6">🏡 Недвижимость</Typography>
                                            <Typography><b>Файл:</b> {finalResult.files[0]}</Typography>
                                            <Typography><b>YOLO:</b> {finalResult.results.real_estate.yolo.class} ({(finalResult.results.real_estate.yolo.confidence * 100).toFixed(2)}%)</Typography>
                                        </CardContent>
                                    </Card>
                                </Grid>
                            )}

                            {enableTech && finalResult.results.tech && (
                                <Grid item xs={12}>
                                    <Card>
                                        <CardContent>
                                            <Typography variant="h6">📱 Техника</Typography>
                                            <Typography><b>Файл:</b> {finalResult.files[1]}</Typography>
                                            <Typography><b>CLIP:</b> {finalResult.results.tech.clip.class} ({(finalResult.results.tech.clip.confidence * 100).toFixed(2)}%)</Typography>
                                        </CardContent>
                                    </Card>
                                </Grid>
                            )}

                            {enableCar && finalResult.results.car && (
                                <Grid item xs={12}>
                                    <Card>
                                        <CardContent>
                                            <Typography variant="h6">🚗 Автомобиль</Typography>
                                            <Typography><b>Файл:</b> {finalResult.files[2]}</Typography>
                                            <Typography><b>ResNet:</b> {finalResult.results.car.resnet.class} ({(finalResult.results.car.resnet.confidence * 100).toFixed(2)}%)</Typography>
                                        </CardContent>
                                    </Card>
                                </Grid>
                            )}

                            {/* 🔹 Общий класс возвращен */}
                            <Grid item xs={12}>
                                <Card>
                                    <CardContent>
                                        <Typography variant="h6">📊 Общий класс</Typography>
                                        <Typography className="final-class">
                                            {finalResult.final_class} ({(finalResult.final_confidence * 100 || 0).toFixed(2)}%)
                                        </Typography>
                                    </CardContent>
                                </Card>
                            </Grid>
                        </Grid>
                    </Box>
                )}
            </Box>
        </div>
    );
};

export default UploadForm;
