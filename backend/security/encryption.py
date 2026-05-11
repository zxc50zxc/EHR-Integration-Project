import base64
import hashlib

from cryptography.fernet import Fernet, InvalidToken

from backend.config import settings


def _fernet_key() -> bytes:
    if settings.ENCRYPTION_KEY:
        return settings.ENCRYPTION_KEY.encode("utf-8")

    digest = hashlib.sha256(settings.SECRET_KEY.encode("utf-8")).digest()
    return base64.urlsafe_b64encode(digest)


def encrypt_data(value: str | None) -> str | None:
    if value is None:
        return None
    return Fernet(_fernet_key()).encrypt(value.encode("utf-8")).decode("utf-8")


def decrypt_data(value: str | None) -> str | None:
    if value is None:
        return None
    try:
        return Fernet(_fernet_key()).decrypt(value.encode("utf-8")).decode("utf-8")
    except InvalidToken:
        return None


encrypt_phi = encrypt_data
decrypt_phi = decrypt_data
