from sqlalchemy import Column, Integer, String
from db import Base, engine

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    password_hash = Column(String, nullable=False)

# Создаем таблицы в базе
Base.metadata.create_all(bind=engine)
