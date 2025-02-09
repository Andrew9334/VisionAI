FROM python:3.9-slim

# Устанавливаем рабочую директорию
WORKDIR /app

# Копируем requirements.txt
COPY requirements.txt /app/
RUN apt-get update && apt-get install -y gcc libpq-dev git \
    && pip install --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt \
    && apt-get remove -y gcc \
    && apt-get autoremove -y \
    && rm -rf /var/lib/apt/lists/*

# Копируем остальные файлы проекта
COPY . /app/

# Указываем команду запуска
CMD ["python", "app/app.py"]

