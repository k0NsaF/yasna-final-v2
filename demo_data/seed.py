
from datetime import datetime, timedelta
from decimal import Decimal

from backend.app.database import Base, engine, SessionLocal
from backend.app.models import (
    Family,
    Child,
    Lesson,
    Booking,
    Attendance,
    Subscription,
    LessonTransaction,
    Payment,
    Notification,
)


def seed_demo_data():
    Base.metadata.create_all(bind=engine)

    db = SessionLocal()

    try:
        # Защита от повторного создания демо-данных.
        demo_phone = "+79990000001"

        existing_family = (
            db.query(Family)
            .filter(Family.phone == demo_phone)
            .first()
        )

        if existing_family:
            print("Демо-данные уже существуют. Повторное создание пропущено.")
            return

        # 1. Семья.
        family = Family(
            name="Демо-семья Ивановых",
            phone=demo_phone,
        )
        db.add(family)
        db.flush()

        # 2. Двое детей.
        child_one = Child(
            family_id=family.id,
            first_name="Александр",
            last_name="Иванов",
            birth_date="2015-04-12",
        )

        child_two = Child(
            family_id=family.id,
            first_name="Мария",
            last_name="Иванова",
            birth_date="2017-09-23",
        )

        db.add_all([child_one, child_two])
        db.flush()

        # 3. Прошедшее занятие для демонстрации посещаемости.
        past_lesson = Lesson(
            title="Демо: изготовление деревянной игрушки",
            description="Демонстрационное групповое занятие",
            starts_at=datetime.now() - timedelta(days=2),
            duration_minutes=90,
            capacity=2,
            price=Decimal("500.00"),
            is_active=True,
        )

        # 4. Будущее занятие для демонстрации записи.
        future_lesson = Lesson(
            title="Демо: создание деревянной машинки",
            description="Будущее занятие для проверки записи",
            starts_at=datetime.now() + timedelta(days=3),
            duration_minutes=90,
            capacity=2,
            price=Decimal("500.00"),
            is_active=True,
        )

        db.add_all([past_lesson, future_lesson])
        db.flush()

        # 5. Абонемент на четыре занятия.
        subscription = Subscription(
            family_id=family.id,
            child_id=child_one.id,
            title="Демо-абонемент на 4 занятия",
            total_lessons=4,
            used_lessons=1,
            price=Decimal("2000.00"),
            expires_at=datetime.now() + timedelta(days=60),
            is_active=True,
        )

        db.add(subscription)
        db.flush()

        # 6. Платёж за абонемент.
        payment = Payment(
            family_id=family.id,
            subscription_id=subscription.id,
            amount=Decimal("2000.00"),
            status="succeeded",
            payment_method="demo",
            credited=True,
        )

        db.add(payment)
        db.flush()

        # 7. История начисления четырёх занятий.
        grant_transaction = LessonTransaction(
            subscription_id=subscription.id,
            booking_id=None,
            amount=4,
            operation="grant",
            reason="Начисление демо-абонемента после оплаты",
        )

        # 8. Списание одного занятия.
        use_transaction = LessonTransaction(
            subscription_id=subscription.id,
            booking_id=None,
            amount=1,
            operation="use",
            reason="Демо-посещение занятия",
        )

        db.add_all([grant_transaction, use_transaction])

        # 9. Запись ребёнка на прошедшее занятие.
        booking = Booking(
            child_id=child_one.id,
            lesson_id=past_lesson.id,
            status="booked",
        )

        db.add(booking)
        db.flush()

        # 10. Отметка о посещении.
        attendance = Attendance(
            booking_id=booking.id,
            status="attended",
            marked_at=datetime.now(),
        )

        db.add(attendance)

        # 11. Уведомление для родителя.
        notification = Notification(
            family_id=family.id,
            title="Добро пожаловать в Ясну!",
            message=(
                "Это демонстрационное уведомление. "
                "Здесь будут появляться сообщения мастерской."
            ),
            is_read=False,
        )

        db.add(notification)

        db.commit()

        print("Демо-данные успешно созданы!")
        print(f"Семья: {family.name}")
        print(f"ID семьи: {family.id}")
        print(f"ID первого ребёнка: {child_one.id}")
        print(f"ID второго ребёнка: {child_two.id}")
        print(f"ID абонемента: {subscription.id}")
        print(f"ID платежа: {payment.id}")
        print(f"ID будущего занятия: {future_lesson.id}")
        print("Остаток абонемента: 3 занятия")

    except Exception:
        db.rollback()
        raise

    finally:
        db.close()


if __name__ == "__main__":
    seed_demo_data()
