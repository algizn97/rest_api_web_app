"""create users accounts payments with test data

Revision ID: 087146bf6192
Revises: 
Create Date: 2026-01-31 13:25:39.971623
"""

from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from passlib.context import CryptContext

# revision identifiers
revision: str = '087146bf6192'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

# Хеши паролей
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
USER_HASH = pwd_context.hash('password123')
ADMIN_HASH = pwd_context.hash('password123')

def upgrade() -> None:
    """✅ Создать таблицы + тестовые данные"""

    # 1. Таблица users
    op.create_table('users',
        sa.Column('id', sa.BigInteger(), autoincrement=True, primary_key=True, index=True),
        sa.Column('email', sa.String(), nullable=False, index=True),
        sa.Column('hashed_password', sa.String(), nullable=False),
        sa.Column('full_name', sa.String(), nullable=False),
        sa.Column('is_admin', sa.Boolean(), default=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('email')
    )

    # 2. Таблица accounts
    op.create_table('accounts',
        sa.Column('id', sa.BigInteger(), autoincrement=True, primary_key=True, index=True),
        sa.Column('user_id', sa.BigInteger(), sa.ForeignKey('users.id'), nullable=False),
        sa.Column('balance', sa.Float(), default=0.0),
        sa.PrimaryKeyConstraint('id')
    )

    # 3. Таблица payments
    op.create_table('payments',
        sa.Column('id', sa.BigInteger(), autoincrement=True, primary_key=True, index=True),
        sa.Column('transaction_id', sa.String(length=36), nullable=False, index=True),
        sa.Column('user_id', sa.BigInteger(), sa.ForeignKey('users.id'), nullable=False),
        sa.Column('account_id', sa.BigInteger(), sa.ForeignKey('accounts.id'), nullable=False),
        sa.Column('amount', sa.Float(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('transaction_id')
    )

    # ✅ ТЕСТОВЫЕ ДАННЫЕ
    op.execute(f"""
        INSERT INTO users (email, hashed_password, full_name, is_admin) VALUES
        ('user@test.com', '{USER_HASH}', 'Test User', false),
        ('admin@test.com', '{ADMIN_HASH}', 'Admin User', true)
        ON CONFLICT DO NOTHING
    """)

    op.execute("""
        INSERT INTO accounts (user_id, balance) VALUES
        ((SELECT id FROM users WHERE email = 'user@test.com'), 0.0),
        ((SELECT id FROM users WHERE email = 'admin@test.com'), 0.0)
        ON CONFLICT DO NOTHING
    """)


def downgrade() -> None:
    """🔄 Откат миграции"""
    op.drop_table('payments')
    op.drop_table('accounts')
    op.drop_table('users')
