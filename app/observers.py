import logging
from .contracts import BookingObserver
log=logging.getLogger("hotel.events")
class EventBus:
    def __init__(self): self.observers=[]
    def subscribe(self,observer): self.observers.append(observer)
    def publish(self,event,payload):
        for observer in list(self.observers): observer.update(event,payload)
class AuditObserver(BookingObserver):
    def update(self,event,payload): log.info("[AuditObserver] %s %s",event,payload)
class NotificationObserver(BookingObserver):
    def update(self,event,payload): log.info("[NotificationObserver] Aviso para reserva %s",payload.get("booking_id"))
