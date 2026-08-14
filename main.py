from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from auth import get_current_user
from routers import users, products
from model import SessionLocal, User, Product
from pydantic import BaseModel
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    )

app.include_router(
    users.router,
    prefix="/users"
)

app.include_router(
    products.router,
    prefix="/products"
)
