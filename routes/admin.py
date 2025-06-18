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

class Pickup(BaseModel):
    pickup_id: int
    timestamp: str
    bin_id: int
    house_id: int
    truck_id: int
    schedule_id: int

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

@admin.post("/add_pickup")
async def add_pickup(info: Pickup):
    try:
        data = {
            "pickup_id": info.pickup_id,
            "timestamp": info.timestamp,
            "bin_id": info.bin_id,
            "house_id": info.house_id,
            "truck_id": info.truck_id,
            "schedule_id": info.schedule_id
        }
        supabase.table("pickups").insert(data).execute()
        return {"message": "Pickup Information Successfully Recorded"}
    except:
        return {"message": "Pickup Information Couldn't be Recorded"}

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

@admin.post("/add_schedule")
async def add_schedule(info: Schedule):
    try:
        data = {
            "schedule_id": info.schedule_id,
            "truck_id": info.truck_id,
            "worker_id": info.worker_id,
            "date": info.date,
            "zone": info.zone
        }
        supabase.table("schedules").insert(data).execute()
        return {"message": "Schedule Information Successfully Recorded"}
    except:
        return {"message": "Schedule Information Couldn't be Recorded"}