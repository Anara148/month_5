import redis
from django.conf import settings


redis_client = redis.Redis(
    host=settings.REDIS_HOST,
    port=settings.REDIS_PORT,
    db=settings.REDIS_DB,
    decode_responses=True
)


def save_confirmation_code(email, code, timeout=300):

    key = f"confirmation_code:{email}"
    redis_client.setex(key, timeout, code)
    return True


def get_confirmation_code(email):

    key = f"confirmation_code:{email}"
    return redis_client.get(key)


def delete_confirmation_code(email):

    key = f"confirmation_code:{email}"
    return redis_client.delete(key)


def verify_and_delete_code(email, code):

    saved_code = get_confirmation_code(email)
    if saved_code and saved_code == code:
        delete_confirmation_code(email)
        return True
    return False