from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, EmailStr, Field
from motor.motor_asyncio import AsyncIOMotorClient
from passlib.context import CryptContext
import os
from dotenv import load_dotenv

load_dotenv()

router = APIRouter()

# MongoDB Setup
MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")

client = AsyncIOMotorClient(MONGO_URI)
db = client["sentimentDB"]
users_collection = db["users"]

# Password Hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Login Request Model
class LoginRequest(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=6)

@router.post("/login")
async def login(user: LoginRequest):
    user_record = await users_collection.find_one({"email": user.email})

    if not user_record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    if not pwd_context.verify(user.password, user_record["password"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect password"
        )

    return {
        "message": "Login successful",
        "user": {
            "id": str(user_record["_id"]),
            "email": user_record["email"],
            "firstName": user_record["first_name"],
            "lastName": user_record["last_name"]
        }
    }
