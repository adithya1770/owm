from fastapi import FastAPI
from routes.auth import auth as auth_router
from routes.user import user as user_router
from routes.admin import admin as admin_router
from jobs import call_bin
from client import supabase
import requests, schedule, threading, time

app = FastAPI()

app.include_router(auth_router, prefix="/auth")
app.include_router(user_router, prefix="/user")
app.include_router(admin_router, prefix="/admin")

app.get("/")
async def home():
    return {"message": "Optimised Waste Management"}

def optimized_schedule():
    try:
        res = requests.post("http://localhost:8000/admin/optimized_schedule")
        print(res.json())
    except Exception as e:
        print(e)

def complete():
    try:
        payload = [info["rfid_tag"] for info in supabase.table("houses").select("rfid_tag").execute().data]
        res = requests.post("http://localhost:8000/admin/schedule_completion", json={"rfid_tag": payload})
        print(res.json())
    except Exception as e:
        print(e)

def update():
    try:
        filled_bins = supabase.table("bins").select("zone").eq("status", "filled").execute().data
        filled_zones = list(set([bin_["zone"] for bin_ in filled_bins]))

        if not filled_zones:
            print("No filled bins found.")
            return
        for zone in filled_zones:
            houses = supabase.table("houses").select("house_id").eq("zone", zone).execute().data
            for house in houses:
                supabase.table("houses").update({"remarks": False}).eq("house_id", house["house_id"]).execute()

        print("Remarks updated for houses in zones with filled bins.")
    except Exception as e:
        print("Error updating remarks:", e)


def run_all_schedulers():
    schedule.every(1).minutes.do(optimized_schedule)
    schedule.every(1).minutes.do(complete)
    schedule.every(1).minutes.do(call_bin)
    schedule.every(1).minutes.do(update)
    
    while True:
        schedule.run_pending()
        time.sleep(1)

threading.Thread(target=run_all_schedulers, daemon=True).start()



