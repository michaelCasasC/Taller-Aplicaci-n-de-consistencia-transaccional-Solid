from .config import DATABASE_URL,PAYMENT_SERVICE_URL
from .repository import PostgresBookingRepository
from .payment import ExternalPaymentProvider,HttpPaymentAdapter,PaymentProxy
from .observers import EventBus,AuditObserver,NotificationObserver
class BookingService:
    def __init__(self,repository,gateway,event_bus):
        self.repository=repository; self.gateway=gateway; self.event_bus=event_bus
    def create_booking(self,data,simulate_error=False):
        return self.repository.create_booking_and_payment(data,self.gateway,self.event_bus,simulate_error)
def build_services():
    bus=EventBus(); bus.subscribe(AuditObserver()); bus.subscribe(NotificationObserver())
    repo=PostgresBookingRepository(DATABASE_URL)
    adapter=HttpPaymentAdapter(ExternalPaymentProvider(PAYMENT_SERVICE_URL))
    return BookingService(repo,PaymentProxy(adapter),bus),repo
