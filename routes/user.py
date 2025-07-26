from fastapi import APIRouter
from client import supabase
from pydantic import BaseModel
from twilio.rest import Client
import os
from dotenv import load_dotenv

load_dotenv()

user = APIRouter()
account_sid = os.getenv("TWILIO_SID")
auth_token = os.getenv("TWILIO_AUTH")

# IF THE USER LOGS IN THEN THESE ARE THE ROUTES SHOWN

class Cookie(BaseModel):
    user_id: str

class House_Cookie(BaseModel):
    house_id: str

class Bill_Cookie(BaseModel):
    house_id: str
    bill_id: str

class Payment(BaseModel):
    amount: int
    card_no: str
    exp_month: int
    exp_year: int
    cvc: int

class Complaint(BaseModel):
    house_id: int
    user_name : str
    complaint: str

class Payment_Cookie(BaseModel):
    house_id: int
    bill_id: int
    mobile: str

@user.post("/me")
async def user_info(cookie: Cookie):
    try:
        response = supabase.table("user_overview").select("*").eq("user_id", cookie.user_id).execute()
        return response.data
        # STORE THE ABOVE RESPONSE JSON IN LOCAL STORAGE FOR FURTHER USE
    except Exception as e:
        return e

@user.post("/house_info")
async def house_information(cookie: House_Cookie):
    try:
        response = supabase.table("houses").select("*").eq("house_id", cookie.house_id).execute()
        return response.data
    except Exception as e:
        return e
    
@user.post("/pickup_info")
async def pickup_information(cookie: House_Cookie):
    try:
        response = supabase.table("pickups").select("*").eq("house_id", cookie.house_id).execute()
        return response.data
    except Exception as e:
        return e
    
@user.post("/billing_info")
async def billing_information(cookie: House_Cookie):
    try:
        response = supabase.table("billing").select("*").eq("house_id", cookie.house_id).execute()
        return response.data
    except Exception as e:
        return e
    
@user.post("/billing_info/payment_status")
async def payment_status(cookie: Bill_Cookie):
    try:
        response = (
            supabase
            .table("billing")
            .select("status")
            .eq("house_id", cookie.house_id)
            .eq("bill_id", cookie.bill_id)
            .execute()
        )

        data = response.data
        if not data:
            return {"status": "No Billing Info Found"}

        status = data[0]["status"].lower()
        if status == "paid":
            return {"status": "Paid"}
        else:
            return {"status": "Not Paid"}

    except Exception as e:
        return {"error": str(e)}

    
@user.post("/billing_info/payment_gateway")
async def payment_gateway(cookie: Payment_Cookie):
    client = Client(account_sid, auth_token)
    try:
        response = supabase.table("billing").select("*").eq("house_id", cookie.house_id).eq("bill_id", cookie.bill_id).execute()
        balance_data = supabase.table("user_overview").select("balance").eq("house_id", cookie.house_id).execute().data

        if not balance_data:
            return {"message": "No balance record found for the house"}

        current_balance = balance_data[0]["balance"]

        if current_balance > 0:
            new_balance = current_balance - 15
            supabase.table("billing").update({"status": "paid"}).eq("house_id", cookie.house_id).eq("bill_id", cookie.bill_id).execute()
            supabase.table("user_overview").update({"balance": new_balance}).eq("house_id", cookie.house_id).execute()
            message = client.messages.create(
                body=f"Bill Amount Paid. Deducted Rs.{new_balance} for House ID {cookie.house_id}",
                from_='+16812442303',
                to="+91"+cookie.mobile
            )
            return {"message": "Payment processed successfully"}
        else:
            message = client.messages.create(
                body="Insufficient balance. Please top-up your Optimized Waste Management account.",
                from_='+16812442303',
                to="+91"+cookie.mobile
            )
            return {"message": "Insufficient balance. Alert sent via SMS."}

    except Exception as e:
        return {"error": str(e)}

@user.post("/greviance/complaint")
async def complaint(data: Complaint):
    try:
        data = {
            "house_id": data.house_id,
            "name": data.user_name,
            "complaint": data.complaint
        }
        supabase.table("complaint").insert(data).execute()
        return {"message": "Succesfully Registered Your Complaint"}
    except Exception as e:
        return {"error": str(e)}
    
@user.post("/greviance/complaint_status")
async def complaint(data: House_Cookie):
    try:
        response = supabase.table("complaint").select("*").eq("house_id", data.house_id).execute()
        response = response.data
        return {"response": response}
    except Exception as e:
        return {"error": str(e)}
