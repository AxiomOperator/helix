import hashlib
import hmac
import secrets


def generate_token() -> str:
    return secrets.token_urlsafe(48)


def hash_token(token: str) -> str:
    return hashlib.sha256(token.encode("utf-8")).hexdigest()


def tokens_match(raw_token: str, token_hash: str) -> bool:
    return secrets.compare_digest(hash_token(raw_token), token_hash)


def derive_csrf_token(session_token: str) -> str:
    digest = hmac.new(session_token.encode("utf-8"), b"linux-command-center-csrf", hashlib.sha256).hexdigest()
    return digest
