from typing import List
from fastapi import APIRouter
from client import supabase
from pydantic import BaseModel

admin = APIRouter()

class House(BaseModel):
    house_id: int
    address: str
    rfid_tag: str
    zone: str
    gps_location: str

class Bin(BaseModel):
    bin_id: int
    status: str
    house_id: int
    fill_level: int
    zone: str

class Billing(BaseModel):
    bill_id: int
    amount: float
    status: str
    house_id: int
    month: str

class Truck(BaseModel):
    truck_id: int
    capacity: float
    gps_location: str

class Worker(BaseModel):
    worker_id: int
    name: str
    availability: str

class Schedule(BaseModel):
    schedule_id: int
    truck_id: int
    worker_id: int
    date: str
    zone: str

class Admin(BaseModel):
    admin_no: int
    admin_name: str

class rfid(BaseModel):
    rfid_tag: List[str]

@admin.get("/user_info")
async def user_information():
    try:
        response = supabase.table("user_overview").select("*").execute()
        return response.data
    except:
        return {"message": "Couldn't Retrive Information"}
    
@admin.get("/house_info")
async def house_information():
    try:
        response = supabase.table("houses").select("""
                *,
                billing(*),
                bins(*),
                pickups(*)
                """).execute()
        return response.data
    except Exception as e:
        return e

@admin.get("/truck_info")
async def truck_information():
    try:
        response = supabase.table("schedules").select("""
                *,
                trucks(*),
                workers(*),
                pickups(*)
                """).execute()
        return response.data
    except Exception as e:
        return e
    
@admin.get("/total_info")
async def total_information():
    try:
        response = supabase.table("schedules").select("""
            *,
            trucks(*),
            workers(*),
            pickups(
                *,
                houses(
                    *,
                    bins(*),
                    billing(*)
                )
            )
        """).execute()
        return response.data
    except Exception as e:
        return e
    
@admin.get("/admin_get")
async def admin_details():
    try:
        response = supabase.table("admin").select("*").execute()
        return response.data
    except:
        return {"message": "Admin Information Couldn't be Retrived"}
    
@admin.post("/add_admin")
async def admin_info(info: Admin):
    try:
        data = {
            "admin_no": info.admin_no,
            "admin_name": info.admin_name
        }
        response = supabase.table("admin").insert(data).execute()
        return {"message": "Admin Information Successfully Recorded"}
    except: 
        return {"message": "Admin Information Couldn't be Recorded"}

@admin.post("/add_house")
async def add_house_information(info: House):
    try:
        data = {
            "house_id": info.house_id,
            "address": info.address,
            "rfid_tag": info.rfid_tag,
            "zone": info.zone,
            "gps_location": info.gps_location
        }
        response = supabase.table("houses").insert(data).execute()
        return {"message": "House Information Successfully Recorded"}
    except: 
        return {"message": "House Information Couldn't be Recorded"}
    
@admin.post("/add_bin")
async def add_bin(info: Bin):
    try:
        data = {
            "bin_id": info.bin_id,
            "status": info.status,
            "house_id": info.house_id,
            "fill_level": info.fill_level,
            "zone": info.zone
        }
        supabase.table("bins").insert(data).execute()
        return {"message": "Bin Information Successfully Recorded"}
    except:
        return {"message": "Bin Information Couldn't be Recorded"}

@admin.post("/add_billing")
async def add_billing(info: Billing):
    try:
        data = {
            "bill_id": info.bill_id,
            "amount": info.amount,
            "status": info.status,
            "house_id": info.house_id,
            "month": info.month
        }
        supabase.table("billing").insert(data).execute()
        return {"message": "Billing Information Successfully Recorded"}
    except:
        return {"message": "Billing Information Couldn't be Recorded"}

@admin.post("/add_truck")
async def add_truck(info: Truck):
    try:
        data = {
            "truck_id": info.truck_id,
            "capacity": info.capacity,
            "gps_location": info.gps_location
        }
        supabase.table("trucks").insert(data).execute()
        return {"message": "Truck Information Successfully Recorded"}
    except:
        return {"message": "Truck Information Couldn't be Recorded"}

@admin.post("/add_worker")
async def add_worker(info: Worker):
    try:
        data = {
            "worker_id": info.worker_id,
            "name": info.name,
            "availability": info.availability
        }
        supabase.table("workers").insert(data).execute()
        return {"message": "Worker Information Successfully Recorded"}
    except:
        return {"message": "Worker Information Couldn't be Recorded"}
    
@admin.get("/free_bins")
async def free_bins():
    try:
        free_bins = []
        response = supabase.table("bins").select("bin_id", "zone", "status").execute()
        response = response.data
        for bins in response:
            if bins["status"].lower() == "filled":
                continue
            else:
                free_bins.append(bins)
        return {"message": free_bins}
    except Exception as e:
        return {"message": str(e)}
    
import math

def haversine_distance(coord1, coord2):
    lat1, lon1 = map(math.radians, coord1)
    lat2, lon2 = map(math.radians, coord2)

    dlat = lat2 - lat1
    dlon = lon2 - lon1

    a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
    c = 2 * math.asin(math.sqrt(a))

    R = 6371 
    return round(R * c, 2)

@admin.post("/optimized_schedule")
async def optimized_schedule():
    try:
        final_schedule = []

        houses = supabase.table("houses").select("house_id, gps_location, zone").execute().data
        trucks = [t for t in supabase.table("trucks").select("truck_id, gps_location, status").execute().data if t["status"]]
        workers = [w for w in supabase.table("workers").select("worker_id, availability").execute().data if w["availability"]]
        bins = [b for b in supabase.table("bins").select("bin_id, zone, status").execute().data if b["status"].lower() != "filled"]

        if not houses or not trucks or not workers or not bins:
            return {"message": "No available trucks, workers, houses, or bins"}

        assignments = []

        for house in houses:
            house_coords = list(map(float, house["gps_location"].split(",")))
            closest_truck = None
            min_distance = float("inf")

            for truck in trucks:
                truck_coords = list(map(float, truck["gps_location"].split(",")))
                distance = haversine_distance(house_coords, truck_coords)

                if distance < min_distance:
                    min_distance = distance
                    closest_truck = truck

            if closest_truck:
                assignments.append({
                    "truck": closest_truck,
                    "house": house,
                    "distance_km": min_distance
                })
                trucks.remove(closest_truck)

        for i, assignment in enumerate(assignments):
            if i >= len(workers) or i >= len(bins):
                break

            schedule_entry = {
                "truck_id": assignment["truck"]["truck_id"],
                "worker_id": workers[i]["worker_id"],
                "zone": assignment["house"]["zone"],
                "bin_id": bins[i]["bin_id"]
            }

            final_schedule.append(schedule_entry)

        if final_schedule:
            supabase.table("schedules").insert(final_schedule).execute()

            for s in final_schedule:
                supabase.table("trucks").update({"status": False}).eq("truck_id", s["truck_id"]).execute()
                supabase.table("workers").update({"availability": False}).eq("worker_id", s["worker_id"]).execute()
                supabase.table("bins").update({"status": "filled"}).eq("bin_id", s["bin_id"]).execute()

            return {"message": "Optimized Schedule Created", "schedule": final_schedule}
        else:
            return {"message": "No schedule could be created"}

    except Exception as e:
        return {"error": str(e)}


@admin.post("/schedule_completion")
async def schedule_completion(tag: rfid):
    try:
        schedule_result = supabase.table("schedules").select("schedule_id", "zone", "truck_id", "worker_id", "bin_id").order("schedule_id", desc=True).limit(1).execute()
        print(schedule_result)
        if not schedule_result.data:
            return {"message": "No schedule found"}
        latest_schedule = schedule_result.data[0]
        data_zone = latest_schedule["zone"]
        inserted_pickups = []
        for code in tag.rfid_tag:
            house_result = supabase.table("houses").select("house_id", "zone").eq("zone", data_zone).eq("rfid_tag", code).execute()
            if house_result.data:
                house = house_result.data[0]
                pickup_data = {
                    "house_id": house["house_id"],
                    "bin_id": latest_schedule["bin_id"],
                    "truck_id": latest_schedule["truck_id"],
                }
                billing_info = {
                    "house_id": house["house_id"],
                    "status": "unpaid"
                }
                supabase.table("pickups").insert(pickup_data).execute()
                inserted_pickups.append(pickup_data)

        supabase.table("schedules").delete().eq("schedule_id", latest_schedule["schedule_id"]).execute()
        supabase.table("trucks").update({"status": True}).eq("truck_id", latest_schedule["truck_id"]).execute()
        supabase.table("bins").update({"status": "not filled"}).eq("bin_id", latest_schedule["bin_id"]).execute()
        supabase.table("workers").update({"availability": True}).eq("worker_id", latest_schedule["worker_id"]).execute()
        supabase.table("billing").insert(billing_info).execute()
        return {"message": "Garbage Routine Completed", "pickups": inserted_pickups}

    except Exception as e:
        return {"error": str(e)}
    
