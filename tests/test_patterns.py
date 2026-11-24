import unittest
from decimal import Decimal
from app.circuit_breaker import CircuitBreaker
from app.observers import EventBus
from app.payment import PaymentProxy,FakePaymentGateway
class Observer:
    def __init__(self): self.events=[]
    def update(self,e,p): self.events.append((e,p))
class Tests(unittest.TestCase):
    def test_observer_two_subscribers(self):
        b=EventBus(); a=Observer(); c=Observer(); b.subscribe(a); b.subscribe(c)
        b.publish("BOOKING_CONFIRMED",{"booking_id":1})
        self.assertEqual(len(a.events),1); self.assertEqual(len(c.events),1)
    def test_proxy(self):
        self.assertTrue(PaymentProxy(FakePaymentGateway()).pay(Decimal("5"),1)["approved"])
    def test_breaker_opens(self):
        b=CircuitBreaker(threshold=2,recovery=0)
        for _ in range(2):
            with self.assertRaises(RuntimeError): b.call(lambda: (_ for _ in ()).throw(RuntimeError()))
        self.assertEqual(b.state,b.OPEN)
if __name__=="__main__": unittest.main()
