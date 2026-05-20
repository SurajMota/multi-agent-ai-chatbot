# backend/server/utils.py
import re
from datetime import datetime

PHONE_RE = re.compile(r"(\+?\d[\d\-\s]{7,}\d)")
EMAIL_RE = re.compile(r"[a-zA-Z0-9._%+-]+@[a-zA-Z.-]+\.[a-zA-Z]{2,}")

def extract_phone(text: str):
    if not text:
        return None
    m = PHONE_RE.search(text)
    return m.group(1).strip() if m else None

def extract_email(text: str):
    if not text:
        return None
    m = EMAIL_RE.search(text)
    return m.group(0).strip() if m else None

def now_date():
    return datetime.utcnow().strftime("%Y-%m-%d")

# -----------------------------
# TIMESTAMP GENERATOR
# -----------------------------
def now_timestamp():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

