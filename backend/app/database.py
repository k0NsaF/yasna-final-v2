
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

# Где будет храниться наша база данных.
# Файл yasna.db появится в корневой папке проекта.
DATABASE_URL = "sqlite:///./yasna.db"

# Создаём подключение к базе данных.
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False}
)

# Создаём фабрику подключений к базе.
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

# Общий класс, от которого будут создаваться таблицы.
Base = declarative_base()


# Функция для получения подключения в API.
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
