import time
from collections import defaultdict, deque
import logging

logger = logging.getLogger(__name__)

class RateLimiter:
    def __init__(self, max_requests_per_minute=10):
        self.max_requests = max_requests_per_minute
        self.requests = defaultdict(deque)
    
    def is_allowed(self, phone_number):
        """
        Check if the phone number is allowed to make a request.
        Returns True if allowed, False if rate limited.
        """
        now = time.time()
        user_requests = self.requests[phone_number]
        
        # Remove requests older than 1 minute
        while user_requests and user_requests[0] < now - 60:
            user_requests.popleft()
        
        # Check if user has exceeded rate limit
        if len(user_requests) >= self.max_requests:
            logger.warning(f"Rate limit exceeded for {phone_number}")
            return False
        
        # Add current request
        user_requests.append(now)
        return True
    
    def get_remaining_requests(self, phone_number):
        """Get the number of remaining requests for a phone number."""
        now = time.time()
        user_requests = self.requests[phone_number]
        
        # Remove old requests
        while user_requests and user_requests[0] < now - 60:
            user_requests.popleft()
        
        return max(0, self.max_requests - len(user_requests))
