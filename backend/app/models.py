
from datetime import datetime

from sqlalchemy import (
    Column,
    Integer,
    String,
    Boolean,
    DateTime,
    ForeignKey,
    UniqueConstraint,
    Text,
    Numeric
)

from sqlalchemy.orm import relationship

from .database import Base


# 1. Семьи
class Family(Base):
    __tablename__ = "families"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(150), nullable=False)
    phone = Column(String(30), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    children = relationship("Child", back_populates="family")
    tokens = relationship("FamilyToken", back_populates="family")


# 2. Дети
class Child(Base):
    __tablename__ = "children"

    id = Column(Integer, primary_key=True, index=True)
    family_id = Column(Integer, ForeignKey("families.id"), nullable=False)
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=True)
    birth_date = Column(String(20), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    family = relationship("Family", back_populates="children")
    bookings = relationship("Booking", back_populates="child")


# 3. Защищённые ссылки для родителей
class FamilyToken(Base):
    __tablename__ = "family_tokens"

    id = Column(Integer, primary_key=True, index=True)
    family_id = Column(Integer, ForeignKey("families.id"), nullable=False)
    token_hash = Column(String(64), unique=True, nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    revoked_at = Column(DateTime, nullable=True)

    family = relationship("Family", back_populates="tokens")


# 4. Занятия
class Lesson(Base):
    __tablename__ = "lessons"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(150), nullable=False)
    description = Column(Text, nullable=True)
    starts_at = Column(DateTime, nullable=False)
    duration_minutes = Column(Integer, default=60)
    capacity = Column(Integer, nullable=False)
    price = Column(Numeric(10, 2), default=0)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    bookings = relationship("Booking", back_populates="lesson")


# 5. Записи детей на занятия
class Booking(Base):
    __tablename__ = "bookings"

    id = Column(Integer, primary_key=True, index=True)
    child_id = Column(Integer, ForeignKey("children.id"), nullable=False)
    lesson_id = Column(Integer, ForeignKey("lessons.id"), nullable=False)
    status = Column(String(20), default="booked")
    created_at = Column(DateTime, default=datetime.utcnow)

    __table_args__ = (
        UniqueConstraint(
            "child_id",
            "lesson_id",
            name="unique_child_lesson_booking"
        ),
    )

    child = relationship("Child", back_populates="bookings")
    lesson = relationship("Lesson", back_populates="bookings")
    attendance = relationship(
        "Attendance",
        back_populates="booking",
        uselist=False
    )


# 6. Посещения
class Attendance(Base):
    __tablename__ = "attendance"

    id = Column(Integer, primary_key=True, index=True)
    booking_id = Column(
        Integer,
        ForeignKey("bookings.id"),
        unique=True,
        nullable=False
    )
    status = Column(String(20), nullable=False)
    marked_at = Column(DateTime, default=datetime.utcnow)

    booking = relationship("Booking", back_populates="attendance")


# 7. История изменения посещений
class AttendanceHistory(Base):
    __tablename__ = "attendance_history"

    id = Column(Integer, primary_key=True, index=True)
    attendance_id = Column(
        Integer,
        ForeignKey("attendance.id"),
        nullable=False
    )
    old_status = Column(String(20), nullable=True)
    new_status = Column(String(20), nullable=False)
    changed_at = Column(DateTime, default=datetime.utcnow)
    comment = Column(Text, nullable=True)


# 8. Абонементы
class Subscription(Base):
    __tablename__ = "subscriptions"

    id = Column(Integer, primary_key=True, index=True)
    family_id = Column(Integer, ForeignKey("families.id"), nullable=False)
    child_id = Column(Integer, ForeignKey("children.id"), nullable=True)
    title = Column(String(150), nullable=False)
    total_lessons = Column(Integer, nullable=False)
    used_lessons = Column(Integer, default=0)
    price = Column(Numeric(10, 2), nullable=False)
    expires_at = Column(DateTime, nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)


# 9. История списаний и начислений занятий
class LessonTransaction(Base):
    __tablename__ = "lesson_transactions"

    id = Column(Integer, primary_key=True, index=True)
    subscription_id = Column(
        Integer,
        ForeignKey("subscriptions.id"),
        nullable=False
    )
    booking_id = Column(
        Integer,
        ForeignKey("bookings.id"),
        nullable=True
    )
    amount = Column(Integer, nullable=False)
    operation = Column(String(20), nullable=False)
    reason = Column(String(200), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)


# 10. Оплаты
class Payment(Base):
    __tablename__ = "payments"

    id = Column(Integer, primary_key=True, index=True)
    family_id = Column(Integer, ForeignKey("families.id"), nullable=False)
    subscription_id = Column(
        Integer,
        ForeignKey("subscriptions.id"),
        nullable=True
    )
    amount = Column(Numeric(10, 2), nullable=False)
    status = Column(String(20), default="pending")
    payment_method = Column(String(30), default="demo")
    external_payment_id = Column(String(150), unique=True, nullable=True)
    credited = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)


# 11. Чеки
class Receipt(Base):
    __tablename__ = "receipts"

    id = Column(Integer, primary_key=True, index=True)
    payment_id = Column(
        Integer,
        ForeignKey("payments.id"),
        nullable=False
    )
    file_path = Column(String(500), nullable=True)
    receipt_url = Column(String(1000), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)


# 12. Уведомления
class Notification(Base):
    __tablename__ = "notifications"

    id = Column(Integer, primary_key=True, index=True)
    family_id = Column(Integer, ForeignKey("families.id"), nullable=False)
    title = Column(String(200), nullable=False)
    message = Column(Text, nullable=False)
    is_read = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
