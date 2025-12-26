from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy import create_engine, text, select, update, ForeignKey
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship, sessionmaker, Session
from sqlalchemy.exc import SQLAlchemyError
from contextlib import contextmanager
from typing import List
from pydantic import BaseModel

SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}, future=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine, class_=Session)

app = FastAPI(title="Транзакции с FastAPI и SQLAlchemy")

class Base(DeclarativeBase):
    pass

class UserDB(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    name: Mapped[str] = mapped_column(index=True)
    email: Mapped[str] = mapped_column(unique=True, index=True)
    balance: Mapped[float] = mapped_column(default=0.0)

    orders = relationship("OrderDB", back_populates="user")

class OrderDB(Base):
    __tablename__ = "orders"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    product_name: Mapped[str] = mapped_column(index=True)
    amount: Mapped[float] = mapped_column()
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))

    user = relationship("UserDB", back_populates="orders")

Base.metadata.create_all(bind=engine)

class User(BaseModel):
    id: int
    name: str
    email: str
    balance: float

    model_config = {"from_attributes": True}

class UserCreate(BaseModel):
    name: str
    email: str
    balance: float = 0.0

class Order(BaseModel):
    id: int
    product_name: str
    amount: float
    user_id: int

    model_config = {"from_attributes": True}

class OrderCreate(BaseModel):
    product_name: str
    amount: float
    user_id: int

class TransactionRequest(BaseModel):
    from_user_id: int
    to_user_id: int
    amount: float
