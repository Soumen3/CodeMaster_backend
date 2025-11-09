from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from app.routes import auth_google, auth_github, problems, tags, constraints, compile_problem, submissions, auth
from app.database.connection import init_db
import os
from fastapi.responses import JSONResponse


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Initialize database tables
    init_db()
    yield
    # Shutdown: cleanup code can go here if needed


app = FastAPI(lifespan=lifespan)

# Configure CORS
origins = [
    "http://localhost:5173",  # Vite default port
    "http://localhost:3000",  # Alternative frontend port
    os.getenv("FRONTEND_URL", "http://localhost:5173"),  # From environment variable
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],  # Allow all methods (GET, POST, PUT, DELETE, etc.)
    allow_headers=["*"],  # Allow all headers
)

# include auth routes
app.include_router(auth.router)
app.include_router(auth_google.router)
app.include_router(auth_github.router)

# include problem routes
app.include_router(problems.router)

# include tag routes
app.include_router(tags.router)

# include constraint routes
app.include_router(constraints.router)

# include compile problem routes
app.include_router(compile_problem.router)

# include submission routes
app.include_router(submissions.router)


@app.get("/")
async def read_root():
    return JSONResponse(content={"message": "Welcome to the CodeMaster Backend API"})
