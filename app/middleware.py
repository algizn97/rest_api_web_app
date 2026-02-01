import jwt
from app.auth import SECRET_KEY, ALGORITHM


async def auth_middleware(request):
    """JWT middleware"""
    auth_header = request.headers.get('Authorization')

    if auth_header and auth_header.startswith('Bearer '):
        try:
            token = auth_header.split(' ')[1]
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            request.ctx.user_id = payload['user_id']
            request.ctx.is_admin = payload.get('is_admin', False)
        except jwt.InvalidTokenError:
            pass
