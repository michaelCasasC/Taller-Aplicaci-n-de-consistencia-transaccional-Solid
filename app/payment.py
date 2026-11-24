from decimal import Decimal
import requests
from .contracts import PaymentGateway
from .circuit_breaker import CircuitBreaker
class FakePaymentGateway(PaymentGateway):
    def pay(self,amount:Decimal,booking_id:int):
        return {"approved":True,"reference":f"FAKE-{booking_id}"}
class ExternalPaymentProvider:
    # Interfaz externa deliberadamente distinta: executeTransaction(value, code).
    def __init__(self,url): self.url=url.rstrip("/")
    def executeTransaction(self,value,code):
        r=requests.post(self.url+"/execute",json={"value":float(value),"code":str(code)},timeout=3)
        r.raise_for_status(); return r.json()
class HttpPaymentAdapter(PaymentGateway):
    def __init__(self,provider,breaker=None):
        self.provider=provider; self.breaker=breaker or CircuitBreaker()
    def pay(self,amount,booking_id):
        return self.breaker.call(lambda:self.provider.executeTransaction(float(amount),str(booking_id)))
class PaymentProxy(PaymentGateway):
    def __init__(self,real_gateway): self.real_gateway=real_gateway
    def pay(self,amount,booking_id):
        if amount<=0: raise ValueError("El pago debe ser mayor que cero")
        print(f"[PaymentProxy] Audita e intercepta pago reserva {booking_id}: {amount}")
        result=self.real_gateway.pay(amount,booking_id)
        print(f"[PaymentProxy] Resultado: {result}")
        return result
