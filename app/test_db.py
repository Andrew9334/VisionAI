from db import SessionLocal
from models import User

# Открываем сессию
db = SessionLocal()

try:
    # Пробуем запросить пользователей
    users = db.query(User).all()
    print("Подключение успешно! Найдено пользователей:", len(users))
except Exception as e:
    print("Ошибка подключения к БД:", e)
finally:
    db.close()
