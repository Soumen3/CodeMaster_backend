from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI
from contextlib import asynccontextmanager
from app.routes import auth_google, auth_github
from app.database.connection import init_db


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Initialize database tables
    init_db()
    yield
    # Shutdown: cleanup code can go here if needed


app = FastAPI(lifespan=lifespan)

# include auth routes
app.include_router(auth_google.router)
app.include_router(auth_github.router)


@app.get("/")
async def read_root():
    return {"Hello": "World"}
