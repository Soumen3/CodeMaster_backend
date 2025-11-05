from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI
from app.routes import auth_google

app = FastAPI()

# include auth routes
app.include_router(auth_google.router)


@app.get("/")
async def read_root():
    return {"Hello": "World"}
