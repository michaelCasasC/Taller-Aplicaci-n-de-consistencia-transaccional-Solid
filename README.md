# Hotel Booking – Michael Alejandro Casas Castaño

**Base asignada:** Hotel Booking. **Tablas:** Guests, Rooms, Bookings, Payments.  
**Stack:** Python 3.12, Flask, PostgreSQL 16, Docker Compose.

> **Nota importante:** el archivo de instrucciones proporcionado solo identifica el nombre de las cuatro tablas; no adjunta el DDL ni el respaldo original de la base Hotel Booking. Este proyecto incluye un esquema PostgreSQL funcional y documentado en `database/schema.sql`. Si el docente entregó un SQL oficial, hay que adaptar este esquema al original antes de entregar.

## Inicio rápido
Requiere Docker Desktop y Docker Compose:
```bash
docker compose up --build
```
Aplicación: http://localhost:5000  
Servicio externo simulado: http://localhost:5001/health
Conexión PostgreSQL desde pgAdmin/DBeaver (host): `127.0.0.1:5433` (la app dentro de Compose sigue conectándose al servicio `db:5432`).

Detener: `docker compose down`. Para reiniciar borrando datos: `docker compose down -v` (no usar durante la prueba de durabilidad).

## Tablas y flujo
- `guests`: huéspedes.
- `rooms`: habitaciones y tarifa.
- `bookings`: reserva, fechas, estado; FK a huésped y habitación.
- `payments`: pago asociado a reserva.

Flujo principal: seleccionar huésped → bloquear habitación → verificar disponibilidad → insertar reserva → procesar pago → insertar pago → confirmar reserva → COMMIT.

## ACID
- **Atomicidad:** `POST /api/bookings` con `"simulate_error": true` provoca una excepción después de insertar la reserva y antes del pago/COMMIT. PostgreSQL revierte todo.
- **Consistencia:** claves foráneas, `CHECK` de fechas y montos, estados permitidos y validación de disponibilidad.
- **Aislamiento:** `SELECT ... FOR UPDATE` bloquea la fila de habitación. Solicitudes concurrentes para la misma habitación se serializan y la segunda vuelve a verificar el solapamiento.
- **Durabilidad:** tras un COMMIT, ejecutar `docker compose restart app` y consultar `GET /api/data`. PostgreSQL conserva los datos en el volumen `hotel_pgdata`.

## CRUD
La interfaz permite registrar y consultar huéspedes, habitaciones, reservas y pagos, además de cancelar reservas lógicamente. API documentada en `docs/API.md`.

## SOLID
- **S:** controlador HTTP, `BookingService`, repositorio y observadores tienen responsabilidades separadas.
- **O:** `PaymentGateway` permite añadir pasarelas nuevas sin reescribir el caso de uso.
- **L:** `FakePaymentGateway` y `HttpPaymentAdapter` cumplen el mismo contrato.
- **I:** contratos pequeños `BookingRepository` y `PaymentGateway`.
- **D:** `BookingService` recibe repositorio, gateway y bus de eventos por inyección.

## Patrones
- **Proxy:** `PaymentProxy` valida el monto, audita y delega al gateway real.
- **Observer:** `AuditObserver` y `NotificationObserver` reaccionan a `BOOKING_CONFIRMED`.
- **Adapter:** `HttpPaymentAdapter` transforma `pay(amount, booking_id)` a `executeTransaction(value, code)`.
- **Circuit Breaker:** tres fallos consecutivos abren el circuito; después de 10 segundos pasa a HALF_OPEN y una llamada de prueba exitosa lo cierra.

## Simulaciones
- ROLLBACK: `POST /api/bookings` con `simulate_error: true`.
- Concurrencia: ejecutar `python scripts/concurrency_demo.py` con la app activa (requiere `pip install requests`). Debe haber una respuesta 201 y otra 409 para el mismo cuarto/fechas.
- Circuit Breaker: detener el proveedor con `docker compose stop external-service`, intentar varios pagos, observar OPEN; restaurar con `docker compose start external-service`, esperar 10 segundos y probar otra vez.
- Durabilidad: crear una reserva, reiniciar solo `app`, volver a consultar los datos.

## Restaurar base
El ZIP incluye `database/BD_CasasMichael.sql`, respaldo lógico SQL reproducible:
```bash
docker compose exec -T db psql -U hotel_user -d hotel_booking < database/BD_CasasMichael.sql
```
Para generar el formato custom solicitado después de ejecutar el proyecto:
```bash
docker compose exec -T db pg_dump -U hotel_user -d hotel_booking -F c > database/BD_CasasMichael.backup
```
Restaurar:
```bash
docker compose exec -T db createdb -U hotel_user hotel_restore
docker compose exec -T db pg_restore -U hotel_user -d hotel_restore < database/BD_CasasMichael.backup
```
No se incluye un `.backup` custom ficticio: debe producirse con `pg_dump` desde PostgreSQL en ejecución.

## Informe y entrega
`docs/INFORME_GUIA.md` contiene la estructura para el PDF. La consigna exige capturas reales y enlace al repositorio; deben añadirse después de ejecutar el proyecto. No inventar evidencias. El ZIP conserva fuentes y archivos de reconstrucción; no incluye dependencias ni secretos reales.
