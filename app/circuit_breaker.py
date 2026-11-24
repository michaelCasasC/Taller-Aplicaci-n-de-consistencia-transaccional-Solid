import time
from threading import Lock
class CircuitOpenError(RuntimeError): pass
class CircuitBreaker:
    CLOSED="CLOSED"; OPEN="OPEN"; HALF_OPEN="HALF_OPEN"
    def __init__(self,threshold=3,recovery=10):
        self.threshold=threshold; self.recovery=recovery; self.failures=0
        self.state=self.CLOSED; self.opened_at=0; self.lock=Lock()
    def call(self,operation):
        with self.lock:
            if self.state==self.OPEN:
                if time.monotonic()-self.opened_at>=self.recovery:
                    self.state=self.HALF_OPEN; print("[CircuitBreaker] OPEN -> HALF_OPEN")
                else: raise CircuitOpenError("Circuit Breaker OPEN")
        try: result=operation()
        except Exception:
            with self.lock:
                self.failures+=1
                if self.state==self.HALF_OPEN or self.failures>=self.threshold:
                    self.state=self.OPEN; self.opened_at=time.monotonic(); print("[CircuitBreaker] -> OPEN")
            raise
        with self.lock:
            if self.state==self.HALF_OPEN:
                self.state=self.CLOSED; print("[CircuitBreaker] HALF_OPEN -> CLOSED")
            self.failures=0
        return result
