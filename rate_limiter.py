import time
from collections import defaultdict

class RateLimiter:
    def __init__(self, max_requests_per_minute=10):
        self.max_requests = int(max_requests_per_minute)
        self.calls = defaultdict(list)

    def is_allowed(self, key: str) -> bool:
        now = time.time()
        window_start = now - 60
        lst = self.calls[key]
        while lst and lst[0] < window_start:
            lst.pop(0)
        if len(lst) >= self.max_requests:
            return False
        lst.append(now)
        return True
