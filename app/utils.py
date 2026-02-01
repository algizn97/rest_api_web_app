import hashlib

SALT = "sanic_rest_api_2026"


def simple_hash(password: str) -> str:
    hash_full = hashlib.sha256((password + SALT).encode()).hexdigest()
    return f"$2b$12${hash_full[:53]}"


def verify_password(plain: str, hashed: str) -> bool:
    """Check the password of the user"""
    expected = simple_hash(plain)
    return expected == hashed
