import os
DATABASE_URL=os.getenv("DATABASE_URL","postgresql://hotel_user:local_demo_password@localhost:5432/hotel_booking")
PAYMENT_SERVICE_URL=os.getenv("PAYMENT_SERVICE_URL","http://localhost:5001")
PORT=int(os.getenv("PORT","5000"))
