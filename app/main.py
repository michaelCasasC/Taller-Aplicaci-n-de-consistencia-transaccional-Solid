from datetime import date
import logging
from flask import Flask,jsonify,request,render_template_string,redirect,url_for
from .service import build_services
from .config import PORT
logging.basicConfig(level=logging.INFO,format="%(asctime)s %(levelname)s %(name)s %(message)s")
app=Flask(__name__); service,repo=build_services()
HTML="""<!doctype html><html lang='es'><meta charset='utf-8'><title>Hotel Booking</title>
<style>body{font:15px Arial;background:#f2f5f8;margin:30px;color:#203047}section{background:white;padding:18px;margin:15px 0;border-radius:10px}input,select,button{padding:9px;margin:5px}button{background:#1767a5;color:white;border:0}table{border-collapse:collapse;width:100%}td,th{padding:7px;border-bottom:1px solid #ddd}</style>
<h1>Hotel Booking · Michael Alejandro Casas Castaño</h1><p>PostgreSQL · ACID · SOLID · Proxy · Observer · Adapter · Circuit Breaker</p>
<p>{{message or ''}}</p>
<section><h2>Registrar huésped</h2><form method=post action=/guests><input name=full_name placeholder='Nombre' required><input name=email type=email placeholder='Correo' required><input name=phone placeholder='Teléfono'><button>Guardar</button></form></section>
<section><h2>Registrar habitación</h2><form method=post action=/rooms><input name=room_number placeholder='Número' required><input name=room_type placeholder='Tipo' required><input name=nightly_rate type=number step=.01 min=.01 placeholder='Tarifa' required><button>Guardar</button></form></section>
<section><h2>Crear reserva y pagar</h2><form method=post action=/bookings>
<select name=guest_id>{% for x in guests %}<option value={{x.id}}>{{x.full_name}} (#{{x.id}})</option>{% endfor %}</select>
<select name=room_id>{% for x in rooms %}<option value={{x.id}}>Habitación {{x.room_number}} · ${{x.nightly_rate}}</option>{% endfor %}</select>
Entrada <input name=check_in type=date required> Salida <input name=check_out type=date required><button>Reservar y pagar</button></form></section>
{% for title,rows,cols in datasets %}<section><h2>{{title}}</h2><table><tr>{% for c in cols %}<th>{{c}}</th>{% endfor %}</tr>{% for row in rows %}<tr>{% for c in cols %}<td>{{row.get(c.lower().replace(' ','_'), '')}}</td>{% endfor %}</tr>{% endfor %}</table></section>{% endfor %}
</html>"""
def render(message=None):
    g,r,b,p=repo.list_data()
    return render_template_string(HTML,message=message,guests=g,rooms=r,datasets=[
        ("Huéspedes",g,["ID","Full Name","Email","Phone"]),
        ("Habitaciones",r,["ID","Room Number","Room Type","Nightly Rate","Status"]),
        ("Reservas",b,["ID","Guest Name","Room Number","Check In","Check Out","Total Amount","Status"]),
        ("Pagos",p,["ID","Booking ID","Amount","Method","Status","External Reference"])])
@app.get("/")
def index():
    g,r,b,p=repo.list_data()
    datasets=[("Huéspedes",g,["ID","Full Name","Email","Phone"]),
              ("Habitaciones",r,["ID","Room Number","Room Type","Nightly Rate","Status"]),
              ("Reservas",b,["ID","Guest Name","Room Number","Check In","Check Out","Total Amount","Status"]),
              ("Pagos",p,["ID","Booking ID","Amount","Method","Status","External Reference"])]
    return render_template_string(HTML,message=request.args.get("message"),guests=g,rooms=r,datasets=datasets)
@app.post("/guests")
def guest():
    try: repo.add_guest(request.form["full_name"],request.form["email"],request.form.get("phone")); msg="Huésped registrado"
    except Exception as e: msg=str(e)
    return redirect(url_for("index",message=msg))
@app.post("/rooms")
def room():
    try: repo.add_room(request.form["room_number"],request.form["room_type"],request.form["nightly_rate"]); msg="Habitación registrada"
    except Exception as e: msg=str(e)
    return redirect(url_for("index",message=msg))
@app.post("/bookings")
def booking():
    try:
        d={"guest_id":int(request.form["guest_id"]),"room_id":int(request.form["room_id"]),
           "check_in":date.fromisoformat(request.form["check_in"]),"check_out":date.fromisoformat(request.form["check_out"])}
        result=service.create_booking(d); msg=f"Reserva #{result['booking_id']} confirmada. Total ${result['total']}"
    except Exception as e: msg=f"Reserva no realizada: {e}"
    return redirect(url_for("index",message=msg))
@app.get("/api/health")
def health(): return jsonify(status="ok")
@app.get("/api/data")
def api_data():
    g,r,b,p=repo.list_data()
    def conv(rows): return [{k:(v.isoformat() if hasattr(v,"isoformat") else str(v) if k in ("nightly_rate","total_amount","amount") else v) for k,v in x.items()} for x in rows]
    return jsonify(guests=conv(g),rooms=conv(r),bookings=conv(b),payments=conv(p))
@app.post("/api/bookings")
def api_booking():
    x=request.get_json(force=True)
    try:
        d={"guest_id":int(x["guest_id"]),"room_id":int(x["room_id"]),"check_in":date.fromisoformat(x["check_in"]),"check_out":date.fromisoformat(x["check_out"])}
        return jsonify(service.create_booking(d,bool(x.get("simulate_error",False)))),201
    except Exception as e: return jsonify(error=str(e)),409
@app.post("/api/guests")
def api_guest():
    x=request.get_json(force=True)
    try: return jsonify(guest_id=repo.add_guest(x["full_name"],x["email"],x.get("phone"))),201
    except Exception as e: return jsonify(error=str(e)),400
@app.post("/api/rooms")
def api_room():
    x=request.get_json(force=True)
    try: return jsonify(room_id=repo.add_room(x["room_number"],x["room_type"],x["nightly_rate"])),201
    except Exception as e: return jsonify(error=str(e)),400
@app.post("/api/bookings/<int:bid>/cancel")
def cancel(bid): return jsonify(cancelled=repo.cancel_booking(bid))
if __name__=="__main__": app.run(host="0.0.0.0",port=PORT)
