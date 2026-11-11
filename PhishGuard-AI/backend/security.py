import re
import time
from collections import defaultdict, deque
from fastapi import HTTPException

MESSAGE_ID_RE = re.compile(r"^[A-Za-z0-9_-]{1,200}$")

class InMemoryRateLimiter:
    def __init__(self, limit=60, window_seconds=60):
        self.limit = limit
        self.window_seconds = window_seconds
        self.events = defaultdict(deque)

    def check(self, key: str):
        now = time.monotonic()
        bucket = self.events[key]
        while bucket and now - bucket[0] >= self.window_seconds:
            bucket.popleft()
        if len(bucket) >= self.limit:
            raise HTTPException(status_code=429, detail="Too many requests. Please try again later.")
        bucket.append(now)

rate_limiter = InMemoryRateLimiter()

def validate_message_id(message_id: str) -> str:
    if not MESSAGE_ID_RE.fullmatch(message_id):
        raise HTTPException(status_code=400, detail="Invalid message identifier.")
    return message_id

def validate_bearer(authorization: str | None) -> str:
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Valid authorization is required.")
    token = authorization[7:].strip()
    if not token or len(token) > 4096:
        raise HTTPException(status_code=401, detail="Valid authorization is required.")
    return token
