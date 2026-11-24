-- Respaldo lógico SQL reproducible de Hotel Booking.
-- Para backup PostgreSQL custom real, usar pg_dump -F c según README.
BEGIN;
CREATE TABLE IF NOT EXISTS guests (
 id BIGSERIAL PRIMARY KEY, full_name VARCHAR(150) NOT NULL,
 email VARCHAR(180) NOT NULL UNIQUE, phone VARCHAR(40), created_at TIMESTAMPTZ DEFAULT NOW()
);
CREATE TABLE IF NOT EXISTS rooms (
 id BIGSERIAL PRIMARY KEY, room_number VARCHAR(20) NOT NULL UNIQUE,
 room_type VARCHAR(60) NOT NULL, nightly_rate NUMERIC(12,2) NOT NULL CHECK(nightly_rate>=0),
 status VARCHAR(20) NOT NULL DEFAULT 'AVAILABLE' CHECK(status IN ('AVAILABLE','MAINTENANCE')),
 created_at TIMESTAMPTZ DEFAULT NOW()
);
CREATE TABLE IF NOT EXISTS bookings (
 id BIGSERIAL PRIMARY KEY, guest_id BIGINT NOT NULL REFERENCES guests(id),
 room_id BIGINT NOT NULL REFERENCES rooms(id), check_in DATE NOT NULL, check_out DATE NOT NULL,
 total_amount NUMERIC(12,2) NOT NULL CHECK(total_amount>=0),
 status VARCHAR(20) NOT NULL DEFAULT 'PENDING' CHECK(status IN ('PENDING','CONFIRMED','CANCELLED')),
 created_at TIMESTAMPTZ DEFAULT NOW(), CHECK(check_out>check_in)
);
CREATE TABLE IF NOT EXISTS payments (
 id BIGSERIAL PRIMARY KEY, booking_id BIGINT NOT NULL REFERENCES bookings(id) ON DELETE RESTRICT,
 amount NUMERIC(12,2) NOT NULL CHECK(amount>0), method VARCHAR(30) NOT NULL,
 status VARCHAR(20) NOT NULL CHECK(status IN ('APPROVED','DECLINED')), external_reference VARCHAR(100),
 created_at TIMESTAMPTZ DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS idx_bookings_room_dates ON bookings(room_id,check_in,check_out);
CREATE INDEX IF NOT EXISTS idx_bookings_guest ON bookings(guest_id);
CREATE INDEX IF NOT EXISTS idx_payments_booking ON payments(booking_id);
INSERT INTO guests(full_name,email,phone) VALUES('Huésped de demostración','demo@hotel.local','0990000000') ON CONFLICT(email) DO NOTHING;
INSERT INTO rooms(room_number,room_type,nightly_rate) VALUES('101','Sencilla',45),('102','Doble',70),('201','Suite',120) ON CONFLICT(room_number) DO NOTHING;
COMMIT;
