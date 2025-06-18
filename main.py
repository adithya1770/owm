from fastapi import FastAPI
from routes.auth import auth as auth_router
from routes.user import user as user_router
from routes.admin import admin as admin_router

app = FastAPI()

app.include_router(auth_router, prefix="/auth")
app.include_router(user_router, prefix="/user")
app.include_router(admin_router, prefix="/admin")