from dotenv import load_dotenv
import os
from sqlalchemy import (
    create_engine,
    Column,
    Integer,
    String,
    Numeric,
    DateTime,
    ForeignKey
)
from sqlalchemy.orm import DeclarativeBase, sessionmaker, relationship
from datetime import datetime

load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")

engine = create_engine(DATABASE_URL)

class Base(DeclarativeBase):
    pass

class Vote(Base):
    __tablename__ = "votes"
    user_id = Column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        primary_key=True
    )

    product_id = Column(
        Integer,
        ForeignKey("products.id", ondelete="CASCADE"),
        primary_key=True
        )
    
class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    email = Column(String(100), nullable=False)
    password = Column(String(100), nullable=False)
    created_at = Column(
        DateTime(timezone=True),
          default=datetime.now
          )
    products = relationship("Product", back_populates="owner")

class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    description = Column(String(255), nullable=False)
    price = Column(Numeric, nullable=False)
    quantity = Column(Integer, nullable=False)
    created_at = Column(
        DateTime,
          default=datetime.now
          )

    owner_id = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=True
    )
    owner = relationship("User", back_populates="products")

SessionLocal = sessionmaker(bind=engine)