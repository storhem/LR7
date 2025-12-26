from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy import create_engine, text, select, update, ForeignKey
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship, sessionmaker, Session
from typing import List
from pydantic import BaseModel

SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)

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

def get_db():
    db = SessionLocal()
    try:
        yield db
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()

@app.post("/users/", response_model=User)
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    db_user = UserDB.model_validate(user)
    db.add(db_user)
    return db_user


@app.get("/users/", response_model=List[User])
def read_users(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    users = db.execute(select(UserDB).offset(skip).limit(limit)).scalars().all()
    return users


@app.get("/users/{user_id}", response_model=User)
def read_user(user_id: int, db: Session = Depends(get_db)):
    user = db.execute(select(UserDB).where(UserDB.id == user_id)).scalars().first()
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@app.post("/orders/", response_model=Order)
def create_order(order: OrderCreate, db: Session = Depends(get_db)):
    db_order = OrderDB.model_validate(order)
    db.add(db_order)
    return db_order

@app.get("/orders/", response_model=List[Order])
def read_orders(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    orders = db.execute(select(OrderDB).offset(skip).limit(limit)).scalars().all()
    return orders

@app.post("/transaction/")
def make_transaction(
    transaction: TransactionRequest,
    db: Session = Depends(get_db)
):
    from_user = db.execute(select(UserDB).where(UserDB.id == transaction.from_user_id)).scalars().first()
    to_user = db.execute(select(UserDB).where(UserDB.id == transaction.to_user_id)).scalars().first()

    if not from_user:
        raise HTTPException(status_code=404, detail=f"User with id {transaction.from_user_id} not found")
    if not to_user:
        raise HTTPException(status_code=404, detail=f"User with id {transaction.to_user_id} not found")

    if from_user.balance < transaction.amount:
        raise HTTPException(status_code=400, detail="Insufficient balance")

    from_user.balance -= transaction.amount
    to_user.balance += transaction.amount

    return {
        "success": True,
        "message": f"Transferred {transaction.amount} from user {from_user.id} to user {to_user.id}",
        "from_user_balance": from_user.balance,
        "to_user_balance": to_user.balance
    }

@app.get("/")
def read_root():
    return {"message": "FastAPI + SQLAlchemy Transactions API is running. Use /docs for API documentation"}