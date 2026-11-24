from abc import ABC, abstractmethod
class BookingRepository(ABC):
    @abstractmethod
    def create_booking_and_payment(self,data,gateway,event_bus,simulate_error=False): ...
class PaymentGateway(ABC):
    @abstractmethod
    def pay(self,amount,booking_id): ...
class BookingObserver(ABC):
    @abstractmethod
    def update(self,event,payload): ...
