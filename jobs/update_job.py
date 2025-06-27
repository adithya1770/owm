import requests, time
from client import supabase

schedule_result = supabase.table("schedules").select("truck_id", "truck_coords", "house_coords").order("schedule_id", desc=True).limit(1).execute().data[0]
lat, long = tuple(map(float, schedule_result["truck_coords"].split(",")))

while True:
    lat+=0.01
    long+=0.01
    gps_location = f"{lat:.6f},{long:.6f}"

    payload = {
        "truck_id": int(schedule_result["truck_id"]),
        "coords": gps_location
    }

    response = requests.post("http://localhost:8000/admin/updater", json=payload)
    print(response.json())

    time.sleep(5)