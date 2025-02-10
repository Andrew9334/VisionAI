from db import SessionLocal
from models import User

db = SessionLocal()
users = db.query(User).all()

if users:
    for user in users:
        print(f"ID: {user.id}, Username: {user.username}, Password Hash: {user.password_hash}")
else:
    print("❌ В таблице users нет записей!")

db.close()
