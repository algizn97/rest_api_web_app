from sanic import Blueprint, json
from sqlalchemy import text
from app.database import AsyncSessionLocal

admin_bp = Blueprint('admin')


async def require_admin(request):
    """Check if the user is an admin."""
    user_id = getattr(request.ctx, 'user_id', None)
    is_admin = getattr(request.ctx, 'is_admin', False)

    if not user_id or not is_admin:
        return json({'error': 'Admin access required'}, 403)
    return None


@admin_bp.get('/users')
async def get_users(request):
    """List all users"""
    admin_check = await require_admin(request)
    if admin_check: return admin_check

    async with AsyncSessionLocal() as session:
        result = await session.execute(
            text("""
                SELECT u.user_id, u.email, u.full_name, u.is_admin, 
                       json_agg(json_build_object('account_id', a.account_id, 'balance', a.balance)) as accounts
                FROM users u 
                LEFT JOIN accounts a ON u.user_id = a.user_id 
                GROUP BY u.user_id
                ORDER BY u.created_at DESC
            """)
        )
        users = []
        for row in result.fetchall():
            users.append({
                'id': row.user_id,
                'email': row.email,
                'full_name': row.full_name,
                'is_admin': row.is_admin,
                'accounts': row.accounts or []
            })
        return json({'users': users})


@admin_bp.post('/users')
async def create_user(request):
    """Create a new user"""
    admin_check = await require_admin(request)
    if admin_check: return admin_check

    data = request.json
    email = data.get('email')
    full_name = data.get('full_name', '')
    password = data.get('password')

    if not all([email, password]):
        return json({'error': 'email and password required'}, 400)

    from app.utils import simple_hash
    password_hash = simple_hash(password)

    async with AsyncSessionLocal() as session:
        try:
            result = await session.execute(
                text(
                    "INSERT INTO users (email, full_name, password_hash) VALUES (:email, :full_name, :hash) RETURNING user_id"),
                {'email': email, 'full_name': full_name, 'hash': password_hash}
            )
            user_id = result.scalar()
            await session.commit()
            return json({'id': user_id, 'email': email}, 201)
        except Exception:
            return json({'error': 'User already exists'}, 400)


@admin_bp.put('/users/<user_id:int>')
async def update_user(request, user_id):
    """Update user information"""
    admin_check = await require_admin(request)
    if admin_check: return admin_check

    data = request.json
    async with AsyncSessionLocal() as session:
        await session.execute(
            text("UPDATE users SET email = :email, full_name = :full_name WHERE user_id = :id"),
            {'email': data.get('email'), 'full_name': data.get('full_name'), 'id': user_id}
        )
        await session.commit()
        return json({'message': 'User updated'})


@admin_bp.delete('/users/<user_id:int>')
async def delete_user(request, user_id):
    """Delete a user"""
    admin_check = await require_admin(request)
    if admin_check: return admin_check

    async with AsyncSessionLocal() as session:
        await session.execute(text("DELETE FROM users WHERE user_id = :id"), {'id': user_id})
        await session.commit()
        return json({'message': 'User deleted'})
