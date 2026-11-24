from concurrent.futures import ThreadPoolExecutor
import requests
URL="http://localhost:5000/api/bookings"
payload={"guest_id":1,"room_id":1,"check_in":"2027-02-10","check_out":"2027-02-12"}
def attempt(_):
    r=requests.post(URL,json=payload,timeout=20)
    return r.status_code,r.text
if __name__=="__main__":
    with ThreadPoolExecutor(max_workers=2) as pool:
        for result in pool.map(attempt,range(2)): print(result)
    print("Esperado: una respuesta 201 y otra 409.")
