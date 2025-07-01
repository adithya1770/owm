import requests, time
from client import supabase

def update():
    schedule_result = supabase.table("schedules").select("truck_id", "truck_coords", "house_coords").order("schedule_id", desc=True).limit(1).execute().data[0]

    lat, long = tuple(map(float, schedule_result["truck_coords"].split(",")))
    lat1, long1 = tuple(map(float, schedule_result["house_coords"].split(",")))

    while True:
        if lat1 > lat and long1 > long:
            lat += 0.1
            long += 0.1
        elif lat1 > lat and long1 < long:
            lat += 0.1
            long -= 0.1
        elif lat1 < lat and long1 > long:
            lat -= 0.1
            long += 0.1
        elif lat1 < lat and long1 < long:
            lat -= 0.1
            long -= 0.1
        elif lat1 == lat and long1 == long:
            print("Location Reached")
            break

        gps_location = f"{lat:.6f},{long:.6f}"

        payload = {
            "truck_id": int(schedule_result["truck_id"]),
            "coords": gps_location
        }

        response = requests.post("http://localhost:8000/admin/updater", json=payload)
        print(response.json())
        time.sleep(5)
