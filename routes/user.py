from fastapi import APIRouter
from client import supabase
from pydantic import BaseModel

user = APIRouter()

# IF THE USER LOGS IN THEN THESE ARE THE ROUTES SHOWN

class Cookie(BaseModel):
    user_id: str

class House_Cookie(BaseModel):
    house_id: str

class Payment(BaseModel):
    amount: int
    card_no: str
    exp_month: int
    exp_year: int
    cvc: int

@user.post("/me")
async def user_info(cookie: Cookie):
    try:
        response = supabase.table("user_overview").select("*").eq("user_id", cookie.user_id).execute()
        return response.data
        # STORE THE ABOVE RESPONSE JSON IN LOCAL STORAGE FOR FURTHER USE
    except Exception as e:
        return e

@user.get("/house_info")
async def house_information(cookie: House_Cookie):
    try:
        response = supabase.table("houses").select("*").eq("house_id", cookie.house_id).execute()
        return response.data
    except Exception as e:
        return e
    
@user.get("/pickup_info")
async def pickup_information(cookie: House_Cookie):
    try:
        response = supabase.table("pickups").select("*").eq("house_id", cookie.house_id).execute()
        return response.data
    except Exception as e:
        return e
    
@user.get("/billing_info")
async def billing_information(cookie: House_Cookie):
    try:
        response = supabase.table("billing").select("*").eq("house_id", cookie.house_id).execute()
        return response.data
    except Exception as e:
        return e
    
@user.get("/billing_info/payment_status")
async def payment_status(cookie: House_Cookie):
    try:
        response = supabase.table("billing").select("status").eq("house_id", cookie.house_id).execute()
        if response.data.status.tolower() in ["paid"]:
            return "Paid"
        else:
            return "Not Paid"
    except Exception as e:
        return e
    
