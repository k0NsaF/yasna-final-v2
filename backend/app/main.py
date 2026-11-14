from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .database import Base, engine
from . import models
from .routers import (
    master,
    family,
    lessons,
    bookings,
    attendance,
    subscriptions,
    payments,
    receipts,
    notifications,
    reports
)

app = FastAPI(
    title="Ясна API",
    description="Система записи и учёта занятий столярной мастерской",
    version="1.0.0"
)

# ВАЖНО: Настройки CORS для работы с Hugging Face
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(master.router)
app.include_router(family.router)
app.include_router(lessons.router)
app.include_router(bookings.router)
app.include_router(attendance.router)
app.include_router(subscriptions.router)
app.include_router(payments.router)
app.include_router(receipts.router)
app.include_router(notifications.router)
app.include_router(reports.router)


@app.get("/")
def home():
    return {
        "project": "Ясна",
        "message": "Сервер работает"
    }


@app.get("/api/health")
def health_check():
    return {
        "status": "ok",
        "project": "yasna"
    }


@app.on_event("startup")
def create_database_tables():
    Base.metadata.create_all(bind=engine)