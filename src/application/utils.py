import hashlib
from src.config import settings

def generate_tripcode(username: str, secret: str) -> str:
    raw = f"{username}{secret}{settings.TRIPCODE_SALT}"
    hashed_part = hashlib.sha256(raw.encode()).hexdigest()[:10]
    return f"{username}!{hashed_part}"