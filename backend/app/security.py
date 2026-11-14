
import hashlib
import hmac
import os
import secrets
import time

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from .database import get_db
from .models import FamilyToken


# Для демонстрации задан временный пароль.
# Позже заменим его на значение из .env.
MASTER_PASSWORD = os.getenv("MASTER_PASSWORD", "yasna-demo-2026")

# Временные сессии мастера хранятся в памяти сервера.
# Срок действия одной сессии — 12 часов.
MASTER_SESSION_SECONDS = 12 * 60 * 60
_master_sessions = {}

bearer_scheme = HTTPBearer(auto_error=False)


def hash_token(token: str) -> str:
    """Возвращает SHA-256-хеш токена."""
    return hashlib.sha256(token.encode("utf-8")).hexdigest()


def generate_family_token() -> tuple[str, str]:
    """
    Создаёт случайный токен семьи.
    Возвращает сам токен и его хеш.
    В базе сохраняем только хеш.
    """
    token = secrets.token_urlsafe(32)
    token_hash = hash_token(token)
    return token, token_hash


def create_master_session(password: str) -> str:
    """Проверяет пароль мастера и создаёт временную сессию."""
    if not hmac.compare_digest(password, MASTER_PASSWORD):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Неверный пароль мастера",
        )

    token = secrets.token_urlsafe(32)
    _master_sessions[token] = time.time() + MASTER_SESSION_SECONDS
    return token


def get_current_master(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
) -> bool:
    """Проверяет bearer-токен мастера."""
    if credentials is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Требуется авторизация мастера",
        )

    token = credentials.credentials
    expires_at = _master_sessions.get(token)

    if expires_at is None or expires_at < time.time():
        _master_sessions.pop(token, None)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Сессия мастера недействительна или истекла",
        )

    return True


def get_current_family(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
    db: Session = Depends(get_db),
):
    """Находит семью по активному персональному токену."""
    if credentials is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Требуется персональная ссылка семьи",
        )

    token_hash = hash_token(credentials.credentials)

    family_token = (
        db.query(FamilyToken)
        .filter(FamilyToken.token_hash == token_hash)
        .first()
    )

    if (
        family_token is None
        or not family_token.is_active
        or family_token.revoked_at is not None
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Ссылка недействительна или отозвана",
        )

    return family_token.family
