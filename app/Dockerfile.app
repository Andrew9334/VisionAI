# Используем Python 3.9
FROM python:3.9-slim

# Устанавливаем рабочую директорию
WORKDIR /app

# Устанавливаем необходимые зависимости (включая git)
RUN apt-get update && apt-get install -y git && rm -rf /var/lib/apt/lists/*

# Копируем файлы с зависимостями
COPY requirements.txt .

# Устанавливаем зависимости Python
RUN pip install --no-cache-dir -r requirements.txt

# Копируем весь код приложения
COPY . .

# Запуск приложения
CMD ["python", "app.py"]
