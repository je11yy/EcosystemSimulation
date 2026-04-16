from __future__ import annotations

import base64
import hashlib
import hmac
import json
import secrets
import time

from app.core.config import settings

HASH_ALGORITHM = "pbkdf2_sha256"
HASH_ITERATIONS = 390_000
SALT_BYTES = 16


def _base64_url_encode(value: bytes) -> str:
    return base64.urlsafe_b64encode(value).rstrip(b"=").decode("ascii")


def _base64_url_decode(value: str) -> bytes:
    padding = "=" * (-len(value) % 4)
    return base64.urlsafe_b64decode(value + padding)


def hash_password(password: str) -> str:
    salt = secrets.token_bytes(SALT_BYTES)
    digest = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        salt,
        HASH_ITERATIONS,
    )
    return "$".join(
        [
            HASH_ALGORITHM,
            str(HASH_ITERATIONS),
            _base64_url_encode(salt),
            _base64_url_encode(digest),
        ]
    )


def verify_password(password: str, hashed_password: str) -> bool:
    try:
        algorithm, iterations_raw, salt_raw, digest_raw = hashed_password.split("$", 3)
        if algorithm != HASH_ALGORITHM:
            return False

        iterations = int(iterations_raw)
        salt = _base64_url_decode(salt_raw)
        expected_digest = _base64_url_decode(digest_raw)
    except (ValueError, TypeError):
        return False

    digest = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        salt,
        iterations,
    )
    return hmac.compare_digest(digest, expected_digest)


def create_session_token(user_id: int) -> str:
    payload = {
        "sub": str(user_id),
        "exp": int(time.time()) + settings.auth_token_ttl_seconds,
    }
    body = _base64_url_encode(
        json.dumps(payload, separators=(",", ":"), sort_keys=True).encode("utf-8")
    )
    signature = _sign(body)
    return f"{body}.{signature}"


def read_session_token(token: str) -> int | None:
    try:
        body, signature = token.split(".", 1)
        expected_signature = _sign(body)
        if not hmac.compare_digest(signature, expected_signature):
            return None

        payload = json.loads(_base64_url_decode(body))
        if int(payload["exp"]) < int(time.time()):
            return None
        return int(payload["sub"])
    except (KeyError, TypeError, ValueError, json.JSONDecodeError):
        return None


def _sign(body: str) -> str:
    digest = hmac.new(
        settings.auth_secret_key.encode("utf-8"),
        body.encode("ascii"),
        hashlib.sha256,
    ).digest()
    return _base64_url_encode(digest)
