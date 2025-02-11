# Используем минимальный Python-образ
FROM python:3.11-slim

# Устанавливаем переменную окружения для отключения кеша pip
ENV PIP_NO_CACHE_DIR=1

# Устанавливаем рабочую директорию
WORKDIR /app

# Установка Git перед установкой зависимостей
RUN apt-get update && apt-get install -y git && rm -rf /var/lib/apt/lists/*

# Копируем только requirements.txt (для кеширования слоев)
COPY requirements.txt .

# Устанавливаем зависимости в одном слое
RUN pip install --no-cache-dir -r requirements.txt && rm -rf /root/.cache/pip

# Копируем файлы модели и сам код (после установки зависимостей для максимального кеширования)
COPY services/tf_predict.py .
COPY models/petresnet50_model.keras /app/models/

# Запуск TensorFlow модели
CMD ["python", "tf_predict.py"]
