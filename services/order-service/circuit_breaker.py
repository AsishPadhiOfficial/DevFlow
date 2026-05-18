import time
import asyncio
from enum import Enum
from typing import Callable, Any

class CircuitBreakerState(Enum):
    CLOSED = "CLOSED"
    OPEN = "OPEN"
    HALF_OPEN = "HALF_OPEN"

class CircuitBreakerOpen(Exception):
    pass

class CircuitBreaker:
    def __init__(
        self,
        name: str,
        failure_threshold: int = 5,
        recovery_timeout: int = 30,
        expected_exception: type = Exception
    ):
        self.name = name
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.expected_exception = expected_exception
        
        self.state = CircuitBreakerState.CLOSED
        self.failure_count = 0
        self.last_failure_time = None

    async def call(self, func: Callable, *args, **kwargs) -> Any:
        current_time = time.time()
        
        if self.state == CircuitBreakerState.OPEN:
            if current_time - self.last_failure_time >= self.recovery_timeout:
                self.state = CircuitBreakerState.HALF_OPEN
            else:
                raise CircuitBreakerOpen(f"Circuit {self.name} is OPEN")
        
        try:
            if asyncio.iscoroutinefunction(func):
                result = await func(*args, **kwargs)
            else:
                result = func(*args, **kwargs)
                
            if self.state == CircuitBreakerState.HALF_OPEN:
                self.state = CircuitBreakerState.CLOSED
                self.failure_count = 0
                
            return result
            
        except self.expected_exception as e:
            self.failure_count += 1
            self.last_failure_time = time.time()
            
            if self.state == CircuitBreakerState.HALF_OPEN or self.failure_count >= self.failure_threshold:
                self.state = CircuitBreakerState.OPEN
                
            raise e

    def get_state(self) -> dict:
        next_retry_time = None
        if self.state == CircuitBreakerState.OPEN and self.last_failure_time:
            next_retry_time = self.last_failure_time + self.recovery_timeout
            
        return {
            "name": self.name,
            "state": self.state.value,
            "failure_count": self.failure_count,
            "last_failure_time": self.last_failure_time,
            "next_retry_time": next_retry_time
        }
