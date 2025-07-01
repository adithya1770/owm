from fastapi import FastAPI
from routes.auth import auth as auth_router
from routes.user import user as user_router
from routes.admin import admin as admin_router
from jobs import bin_fill
import schedule, time, threading

app = FastAPI()

app.include_router(auth_router, prefix="/auth")
app.include_router(user_router, prefix="/user")
app.include_router(admin_router, prefix="/admin")

def run_schedule():
    schedule.every(1500).minutes.do(bin_fill)
    while True:
        schedule.run_pending()
        time.sleep(1)

threading.Thread(target=run_schedule, daemon=True).start()
