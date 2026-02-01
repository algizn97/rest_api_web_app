from .utils import simple_hash, verify_password
import jwt
from datetime import datetime, timedelta, timezone
from sqlalchemy import text

SECRET_KEY = "sanic_rest_api_secret_2026"
ALGORITHM = "HS256"


def create_jwt(user: dict) -> str:
    payload = {
        "user_id": user["user_id"],
        "email": user["email"],
        "is_admin": user["is_admin"],
        "exp": datetime.now(timezone.utc) + timedelta(hours=24)
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


async def authenticate(session, email: str, password: str):
    result = await session.execute(
        text("SELECT user_id, email, password_hash, is_admin, full_name FROM users WHERE email = :email"),
        {"email": email}
    )
    db_user = result.fetchone()

    if not db_user:
        return None

    print(f"DB: {db_user.password_hash[:20]} | Expected: {simple_hash(password)[:20]}")

    if verify_password(password, db_user.password_hash):
        return {
            "user_id": db_user.user_id,
            "email": db_user.email,
            "full_name": db_user.full_name or "No name",
            "is_admin": db_user.is_admin
        }
    return None
