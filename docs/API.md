# API
- `GET /api/health`: salud.
- `GET /api/data`: consulta de las cuatro tablas.
- `POST /api/guests`: JSON `{"full_name":"Ana Demo","email":"ana@example.com","phone":"0991234567"}`.
- `POST /api/rooms`: JSON `{"room_number":"301","room_type":"Familiar","nightly_rate":95}`.
- `POST /api/bookings`: JSON `{"guest_id":1,"room_id":1,"check_in":"2027-03-01","check_out":"2027-03-03"}`.
- `POST /api/bookings`: para ROLLBACK, añadir `"simulate_error":true`.
- `POST /api/bookings/1/cancel`: cancelación lógica.
