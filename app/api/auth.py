from sanic import Blueprint, json
from app.auth import authenticate, create_jwt
from app.database import AsyncSessionLocal

auth_bp = Blueprint('auth')


@auth_bp.post('/login')
async def login(request):
    data = request.json
    email = data.get('email')
    password = data.get('password')

    if not email or not password:
        return json({'error': 'Email and password required'}, 400)

    async with AsyncSessionLocal() as session:
        user = await authenticate(session, email, password)

        if not user:
            return json({'error': 'Invalid credentials'}, 401)

        token = create_jwt(user)
        return json({
            'access_token': token,
            'user': {
                'id': user['user_id'],
                'email': user['email'],
                'full_name': user['full_name'],
                'is_admin': user['is_admin']
            }
        })
