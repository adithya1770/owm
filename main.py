from fastapi import FastAPI
from routes.auth import auth as auth_router
from routes.user import user as user_router

app = FastAPI()

app.include_router(auth_router)
app.include_router(user_router)