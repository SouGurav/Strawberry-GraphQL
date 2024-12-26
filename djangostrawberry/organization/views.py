import jwt
from datetime import datetime, timedelta
from djangostrawberry import settings
from django.contrib.auth.models import User


# Generate JWT token
def generate_jwt(user: User) -> str:
    payload = {
        "user_id": user.id,
        "username": user.username,
        "exp": datetime.now() + timedelta(hours=1),  # Token expires in 1 hour
    }
    token = jwt.encode(payload, settings.SECRET_KEY, algorithm="HS256")
    return token

# Decode and verify JWT token
def decode_jwt(token: str) -> User:
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
        user = User.objects.get(id=payload["user_id"])
        return user
    except (jwt.ExpiredSignatureError, jwt.InvalidTokenError, User.DoesNotExist):
        raise Exception("Invalid or expired token.")
