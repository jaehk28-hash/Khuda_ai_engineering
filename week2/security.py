import base64
import hashlib
import hmac
import json
import secrets
import time

from week2.exceptions import InvalidTokenError

# 실제 서비스라면 환경 변수로 주입해야 하지만, 과제 범위에서는 고정 값으로 둔다.
SECRET_KEY = "week2-wordle-secret-key"
TOKEN_TTL_SECONDS = 60 * 60 * 24
PBKDF2_ITERATIONS = 200_000


def hash_password(password: str) -> str:
    salt = secrets.token_bytes(16)
    password_hash = hashlib.pbkdf2_hmac("sha256", password.encode(), salt, PBKDF2_ITERATIONS)
    return f"{salt.hex()}${password_hash.hex()}"


def verify_password(password: str, stored_password_hash: str) -> bool:
    salt_hex, hash_hex = stored_password_hash.split("$")
    salt = bytes.fromhex(salt_hex)
    candidate_hash = hashlib.pbkdf2_hmac("sha256", password.encode(), salt, PBKDF2_ITERATIONS)
    return hmac.compare_digest(candidate_hash.hex(), hash_hex)


def create_access_token(user_id: int, username: str) -> str:
    payload = {"user_id": user_id, "username": username, "issued_at": time.time()}
    payload_b64 = base64.urlsafe_b64encode(json.dumps(payload).encode()).decode()
    signature = hmac.new(SECRET_KEY.encode(), payload_b64.encode(), hashlib.sha256).hexdigest()
    return f"{payload_b64}.{signature}"


def decode_access_token(token: str) -> dict:
    try:
        payload_b64, signature = token.split(".")
    except ValueError:
        raise InvalidTokenError("토큰 형식이 올바르지 않습니다.")

    expected_signature = hmac.new(SECRET_KEY.encode(), payload_b64.encode(), hashlib.sha256).hexdigest()
    if not hmac.compare_digest(signature, expected_signature):
        raise InvalidTokenError("토큰 서명이 유효하지 않습니다.")

    payload = json.loads(base64.urlsafe_b64decode(payload_b64.encode()))
    if time.time() - payload["issued_at"] > TOKEN_TTL_SECONDS:
        raise InvalidTokenError("토큰이 만료되었습니다.")

    return payload
