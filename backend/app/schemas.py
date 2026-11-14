
from datetime import datetime
from decimal import Decimal
from pydantic import BaseModel, ConfigDict, Field, HttpUrl


class ORMModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)


# ---------- СЕМЬИ ----------

class FamilyCreate(BaseModel):
    name: str = Field(min_length=1, max_length=150)
    phone: str | None = Field(default=None, max_length=30)


class FamilyResponse(ORMModel):
    id: int
    name: str
    phone: str | None = None
    created_at: datetime


# ---------- ДЕТИ ----------

class ChildCreate(BaseModel):
    first_name: str = Field(min_length=1, max_length=100)
    last_name: str | None = Field(default=None, max_length=100)
    birth_date: str | None = None


class ChildResponse(ORMModel):
    id: int
    family_id: int
    first_name: str
    last_name: str | None = None
    birth_date: str | None = None
    created_at: datetime


# ---------- ЗАНЯТИЯ ----------

class LessonCreate(BaseModel):
    title: str = Field(min_length=1, max_length=200)
    description: str | None = None
    starts_at: datetime
    duration_minutes: int = Field(default=60, ge=1, le=600)
    capacity: int = Field(ge=1, le=100)
    price: Decimal = Field(default=Decimal("0"), ge=0)


class LessonResponse(ORMModel):
    id: int
    title: str
    description: str | None = None
    starts_at: datetime
    duration_minutes: int
    capacity: int
    price: Decimal
    is_active: bool
    created_at: datetime


class LessonPublicResponse(LessonResponse):
    booked_count: int
    free_places: int


# ---------- ЗАПИСИ ----------

class BookingCreate(BaseModel):
    child_id: int = Field(gt=0)
    lesson_id: int = Field(gt=0)


class BookingResponse(ORMModel):
    id: int
    child_id: int
    lesson_id: int
    status: str
    created_at: datetime


# ---------- ПОСЕЩАЕМОСТЬ ----------

class AttendanceUpdate(BaseModel):
    status: str = Field(pattern="^(attended|missed|cancelled)$")
    comment: str | None = None


class AttendanceResponse(ORMModel):
    id: int
    booking_id: int
    status: str
    marked_at: datetime | None = None


class AttendanceHistoryResponse(ORMModel):
    id: int
    attendance_id: int
    old_status: str | None = None
    new_status: str
    changed_at: datetime
    comment: str | None = None


# ---------- АБОНЕМЕНТЫ ----------

class SubscriptionCreate(BaseModel):
    family_id: int = Field(gt=0)
    child_id: int | None = Field(default=None, gt=0)
    title: str = Field(min_length=1, max_length=150)
    total_lessons: int = Field(ge=1)
    price: Decimal = Field(default=Decimal("0"), ge=0)
    expires_at: datetime | None = None


class SubscriptionResponse(ORMModel):
    id: int
    family_id: int
    child_id: int | None = None
    title: str
    total_lessons: int
    used_lessons: int
    price: Decimal
    expires_at: datetime | None = None
    is_active: bool
    created_at: datetime


class SubscriptionBalance(BaseModel):
    total_lessons: int
    used_lessons: int
    remaining_lessons: int
    money_balance: Decimal = Decimal("0")


# ---------- ПЛАТЕЖИ ----------

class PaymentCreate(BaseModel):
    family_id: int = Field(gt=0)
    subscription_id: int | None = Field(default=None, gt=0)
    amount: Decimal = Field(gt=0)
    payment_method: str = Field(default="demo", max_length=30)


class PaymentResponse(ORMModel):
    id: int
    family_id: int
    subscription_id: int | None = None
    amount: Decimal
    status: str
    payment_method: str
    external_payment_id: str | None = None
    credited: bool
    created_at: datetime


class PaymentStatusUpdate(BaseModel):
    status: str = Field(pattern="^(pending|succeeded|failed|cancelled)$")


# ---------- ЧЕКИ / КВИТАНЦИИ ----------

class ReceiptLinkCreate(BaseModel):
    receipt_url: HttpUrl


class ReceiptResponse(ORMModel):
    id: int
    payment_id: int
    file_path: str | None = None
    receipt_url: str | None = None
    created_at: datetime


# ---------- УВЕДОМЛЕНИЯ ----------

class NotificationResponse(ORMModel):
    id: int
    family_id: int
    title: str
    message: str
    is_read: bool
    created_at: datetime


# ---------- АВТОРИЗАЦИЯ ----------

class MasterLogin(BaseModel):
    password: str = Field(min_length=1, max_length=200)


class MasterLoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class FamilyLinkResponse(BaseModel):
    family_id: int
    access_token: str
    token_type: str = "bearer"
    message: str = "Сохраните ссылку: токен показывается только один раз."


# ---------- ОБЩИЕ ОТВЕТЫ ----------

class MessageResponse(BaseModel):
    message: str


class HealthResponse(BaseModel):
    status: str
    project: str
