from sanic import Blueprint, json
from sqlalchemy import text
from app.database import AsyncSessionLocal

users_bp = Blueprint('users')


@users_bp.get('/me')
async def get_me(request):
    """Details of the current user"""
    user_id = getattr(request.ctx, 'user_id', None)
    if not user_id:
        return json({'error': 'Authentication required'}, 401)

    async with AsyncSessionLocal() as session:
        result = await session.execute(
            text("SELECT user_id, email, full_name, is_admin FROM users WHERE user_id = :id"),
            {"id": user_id}
        )
        user = result.fetchone()
        if not user:
            return json({'error': 'User not found'}, 404)
        return json({
            'id': user.user_id,
            'email': user.email,
            'full_name': user.full_name,
            'is_admin': user.is_admin
        })


@users_bp.get('/accounts')
async def get_accounts(request):
    """List of your accounts"""
    user_id = getattr(request.ctx, 'user_id', None)
    if not user_id:
        return json({'error': 'Authentication required'}, 401)

    async with AsyncSessionLocal() as session:
        result = await session.execute(
            text("SELECT account_id, balance FROM accounts WHERE user_id = :user_id"),
            {"user_id": user_id}
        )
        accounts = [{'account_id': row.account_id, 'balance': float(row.balance)}
                    for row in result.fetchall()]
        return json({'accounts': accounts})


@users_bp.get('/payments')
async def get_payments(request):
    """Payments history"""
    user_id = getattr(request.ctx, 'user_id', None)
    if not user_id:
        return json({'error': 'Authentication required'}, 401)

    async with AsyncSessionLocal() as session:
        result = await session.execute(
            text("""
                SELECT p.payment_id, p.transaction_id, p.account_id, p.amount, p.created_at
                FROM payments p JOIN accounts a ON p.account_id = a.account_id
                WHERE a.user_id = :user_id ORDER BY p.created_at DESC
            """), {"user_id": user_id}
        )
        payments = [{
            'payment_id': row.payment_id,
            'transaction_id': row.transaction_id,
            'account_id': row.account_id,
            'amount': float(row.amount),
            'created_at': row.created_at.isoformat() if row.created_at else None
        } for row in result.fetchall()]
        return json({'payments': payments})
