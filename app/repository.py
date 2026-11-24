from decimal import Decimal
import psycopg
from psycopg.rows import dict_row
from .contracts import BookingRepository
class PostgresBookingRepository(BookingRepository):
    def __init__(self,url): self.url=url
    def connect(self): return psycopg.connect(self.url,row_factory=dict_row)
    def list_data(self):
        with self.connect() as c:
            guests=c.execute("SELECT * FROM guests ORDER BY id").fetchall()
            rooms=c.execute("SELECT * FROM rooms ORDER BY room_number").fetchall()
            bookings=c.execute("""SELECT b.*,g.full_name guest_name,r.room_number FROM bookings b
                JOIN guests g ON g.id=b.guest_id JOIN rooms r ON r.id=b.room_id ORDER BY b.id DESC""").fetchall()
            payments=c.execute("SELECT * FROM payments ORDER BY id DESC").fetchall()
            return guests,rooms,bookings,payments
    def add_guest(self,name,email,phone):
        with self.connect() as c:
            return c.execute("INSERT INTO guests(full_name,email,phone) VALUES(%s,%s,%s) RETURNING id",(name,email,phone)).fetchone()["id"]
    def add_room(self,number,kind,rate):
        with self.connect() as c:
            return c.execute("INSERT INTO rooms(room_number,room_type,nightly_rate) VALUES(%s,%s,%s) RETURNING id",(number,kind,Decimal(str(rate)))).fetchone()["id"]
    def cancel_booking(self,bid):
        with self.connect() as c:
            return c.execute("UPDATE bookings SET status='CANCELLED' WHERE id=%s AND status IN ('PENDING','CONFIRMED') RETURNING id",(bid,)).fetchone() is not None
    def create_booking_and_payment(self,data,gateway,event_bus,simulate_error=False):
        with self.connect() as c:
            with c.transaction():
                room=c.execute("SELECT * FROM rooms WHERE id=%s FOR UPDATE",(data["room_id"],)).fetchone()
                if not room: raise ValueError("Habitación inexistente")
                if room["status"]!="AVAILABLE": raise ValueError("Habitación no disponible")
                if not c.execute("SELECT id FROM guests WHERE id=%s",(data["guest_id"],)).fetchone(): raise ValueError("Huésped inexistente")
                conflict=c.execute("""SELECT id FROM bookings WHERE room_id=%s AND status IN ('PENDING','CONFIRMED')
                    AND check_in < %s AND check_out > %s LIMIT 1""",
                    (data["room_id"],data["check_out"],data["check_in"])).fetchone()
                if conflict: raise ValueError("La habitación ya está reservada en esas fechas")
                days=(data["check_out"]-data["check_in"]).days
                if days<=0: raise ValueError("La salida debe ser posterior a la entrada")
                total=Decimal(room["nightly_rate"])*days
                bid=c.execute("""INSERT INTO bookings(guest_id,room_id,check_in,check_out,total_amount,status)
                    VALUES(%s,%s,%s,%s,%s,'PENDING') RETURNING id""",
                    (data["guest_id"],data["room_id"],data["check_in"],data["check_out"],total)).fetchone()["id"]
                if simulate_error: raise RuntimeError("ERROR SIMULADO: provocar ROLLBACK")
                paid=gateway.pay(total,bid)
                if not paid.get("approved"): raise RuntimeError("Pago rechazado")
                c.execute("""INSERT INTO payments(booking_id,amount,method,status,external_reference)
                    VALUES(%s,%s,'SIMULATED','APPROVED',%s)""",(bid,total,paid.get("reference")))
                c.execute("UPDATE bookings SET status='CONFIRMED' WHERE id=%s",(bid,))
                event={"booking_id":bid,"guest_id":data["guest_id"],"room_id":data["room_id"]}
            event_bus.publish("BOOKING_CONFIRMED",event)
            return {"booking_id":bid,"total":str(total),"status":"CONFIRMED"}
