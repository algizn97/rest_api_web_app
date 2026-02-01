from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from passlib.context import CryptContext
from sqlalchemy import text
import os
from models import Base
from utils import simple_hash

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql+asyncpg://postgres:password@localhost:5432/rest_api_db")
engine = create_async_engine(DATABASE_URL, echo=True)
AsyncSessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


async def init_db():
    """Create tables"""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def create_test_data():
    """Test data"""
    async with AsyncSessionLocal() as session:
        # User
        user_hash = simple_hash("password123")
        await session.execute(text("""
            INSERT INTO users (email, full_name, password_hash, is_admin) 
            VALUES ('user@test.com', 'Test User', :hash, false)
            ON CONFLICT (email) DO NOTHING
        """), {"hash": user_hash})

        # Admin
        admin_hash = pwd_context.hash("admin123")
        await session.execute(text("""
            INSERT INTO users (email, full_name, password_hash, is_admin) 
            VALUES ('admin@test.com', 'Admin User', :hash, true)
            ON CONFLICT (email) DO NOTHING
        """), {"hash": admin_hash})

        # User account
        await session.execute(text("""
            INSERT INTO accounts (user_id, balance) 
            SELECT user_id, 0.0 FROM users WHERE email='user@test.com'
            ON CONFLICT DO NOTHING
        """))

        await session.commit()


async def dispose_db():
    await engine.dispose()
