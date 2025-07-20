from fastapi import APIRouter
from client import supabase
from pydantic import BaseModel
import jwt
import bcrypt

auth = APIRouter()

class Credentials_Signup(BaseModel):
    email: str
    password: str
    phone_no: str
    display_name: str
    house_id: str
    address: str

class Credentials_Signin(BaseModel):
    email: str
    password: str

class Credentials_Admin(BaseModel):
    admin_id: str
    admin_name: str

class Credentials_Phone_Signup(BaseModel):
    phone: str
    password: str
    email: str
    display_name: str
    house_id: str
    address: str

class Credentials_Phone_Signin(BaseModel):
    phone: str
    password: str

class Phone_Verification(BaseModel):
    phone: str
    token: str

class Email(BaseModel):
    email: str

class Password(BaseModel):
    password: str


# PASSWORD AND CREDENTIALS RESET

@auth.post("/password_reset")
async def reset_password(creds: Email):
    try:
        supabase.auth.reset_password_email(
            creds.email,
            {'redirect_to':'/password_reset/change_password'}
        )
        return {"success": "Password Reset Request Sent"}
    except Exception as e:
        return {"failed": str(e)}
    
@auth.post("password_reset/change_password")
async def change_password(creds: Password):
    try:
        supabase.auth.update_user({'password': creds.password})
        return {"success": "Password Reset Successful"}
    except Exception as e:
        return {"failed": str(e)}
    



# CUSTOMER SIGNUP AND VERIFICATION



@auth.post("/customer_verify")
async def customer_verify(creds: Phone_Verification):
    try:
        supabase.auth.verify_otp({
                'phone': ("91"+creds.phone),
                'token': creds.token,
                'type': "sms"
        })
        return {"success": "You are Successfully Verified"}
    except Exception as e:
        return {"failed": str(e)}
    
@auth.post("/customer_signup_phone")
async def customer_signup_phone(creds: Credentials_Phone_Signup):
    try:
        data = supabase.auth.sign_up({
            'phone': ("91"+creds.phone),
            'password': creds.password
        })
        user = data.user.id
        password_new = bcrypt.hashpw(creds.password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        user_creds = {
            "user_id": user,
            "house_id": int(creds.house_id),
            "phone_no": "91"+creds.phone,
            "display_name": creds.display_name,
            "email": creds.email,
            "password": password_new,
            "address": creds.address
        }
        response = supabase.table("user_overview").insert(user_creds).execute()
        return {"success": "You are Successfully Signed Up. Wait for Verification", "token": user}
    except:
        return {"failed": "Your House is Not Yet Registered"}    
    
@auth.post("/customer_signin_phone")
async def customer_signin_phone(creds: Credentials_Phone_Signin):
    try:
        supabase.auth.sign_in_with_password({
                'phone': creds.phone,
                'password': creds.password
            })
        return {"success": "You are Successfully Signed In"}
    except Exception as e:
        return {"failed": str(e)}    

@auth.post("/customer_signup")
async def customer_signup(creds: Credentials_Signup):
    try:
        data = supabase.auth.sign_up({
            'email': creds.email,
            'password': creds.password,
            'options': {
                "data": {
                    "phone":creds.phone_no,
                    "display_name": creds.display_name
                }
            },
        })
        user = data.user.id
        print(user)
        password_new = bcrypt.hashpw(creds.password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        user_creds = {
            "user_id": user,
            "house_id": int(creds.house_id),
            "phone_no": "91"+creds.phone_no,
            "display_name": creds.display_name,
            "email": creds.email,
            "password": password_new,
            "address": creds.address,
        }
        response = supabase.table("user_overview").insert(user_creds).execute()
        return {"success": "You are Successfully Signed Up. Wait for Verification", "token": user}
    except Exception as e:
        return {"failed": str(e)}

@auth.post("/customer_signin")
async def customer_signin(creds: Credentials_Signin):
    try:
        data = supabase.auth.sign_in_with_password({
            'email': creds.email,
            'password': creds.password,
        })
        result = supabase.table("user_overview").select("user_id").eq("email", creds.email).execute()

        if not result.data:
            return {"failed": "User not found in user_overview"}

        user_id = result.data[0]["user_id"]
        return {"success": "You are Successfully Signed In", "token": user_id}

    except Exception as e:
        return {"failed": str(e)}

    


# ADMIN ROUTES
    


@auth.post("/admin_signup")
async def admin_signup(creds: Credentials_Admin):
    try:
        admin_creds = {
            "admin_id": creds.admin_id,
            "admin_name": creds.admin_name
        }
        response = supabase.table("admin").insert(admin_creds).execute()
        return {"success": "Admin Credentials Added Successfully"}
    except:
        return {"failed": "Admin Details Could not be Added"}

@auth.post("/admin_signin")
async def admin_signin(creds: Credentials_Admin):
    try:
        response = supabase.table("admin").select("*").execute()
        for records in response:
            if creds.admin_id==records["admin_id"] and creds.admin_name==records["admin_name"]:
                token=jwt.encode({"user_id": creds.admin_id}, "secret_key", algorithm="HS256")
                return {"message": "Successful Login", "token": token}
            else:
                return {"message": "Unsucessful Login"}
    except:
        return {"message": "Unexpected Server Error Occurred"}