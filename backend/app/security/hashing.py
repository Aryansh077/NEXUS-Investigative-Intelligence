import hashlib
from pathlib import Path
import bcrypt

def sha256_file(path: str) -> str:
    """Generate SHA-256 hash of a file for tamper-evident provenance."""
    h = hashlib.sha256()
    with Path(path).open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()

def sha256_text(text: str) -> str:
    """Generate SHA-256 hash of text content."""
    return hashlib.sha256(text.encode("utf-8")).hexdigest()

def hash_password(password: str) -> str:
    """Bcrypt password hashing."""
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode("utf-8")[:72], salt).decode("utf-8")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify plain password against bcrypt hash."""
    try:
        return bcrypt.checkpw(
            plain_password.encode("utf-8")[:72],
            hashed_password.encode("utf-8")
        )
    except Exception:
        return False
