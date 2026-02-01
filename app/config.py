import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    DATABASE_URL = os.getenv('DATABASE_URL', 'postgresql+asyncpg://postgres:password@localhost:5432/appdb')
    SECRET_KEY = os.getenv('SECRET_KEY', 'gfdmhghif38yrf9ew0jkf32')
    JWT_SECRET = os.getenv('JWT_SECRET', 'super-secret-jwt-key-2026-change-in-production')
    ALGORITHM = os.getenv('ALGORITHM', 'HS256')


config = Config()
