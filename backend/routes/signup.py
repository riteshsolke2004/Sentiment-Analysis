from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, EmailStr, Field, validator
from motor.motor_asyncio import AsyncIOMotorClient
from bson.objectid import ObjectId
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

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# User schema
class UserSignup(BaseModel):
    firstName: str = Field(..., min_length=1)
    lastName: str = Field(..., min_length=1)
    email: EmailStr
    password: str = Field(..., min_length=6)
    confirmPassword: str

    @validator("confirmPassword")
    def passwords_match(cls, v, values):
        if "password" in values and v != values["password"]:
            raise ValueError("Passwords do not match")
        return v

# Utility
async def is_email_taken(email: str) -> bool:
    existing_user = await users_collection.find_one({"email": email})
    return existing_user is not None

@router.post("/signup", status_code=201)
async def signup(user: UserSignup):
    # Check if email already exists
    if await is_email_taken(user.email):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email already registered."
        )

    # Hash the password
    hashed_password = pwd_context.hash(user.password)

    user_dict = {
        "first_name": user.firstName,
        "last_name": user.lastName,
        "email": user.email,
        "password": hashed_password
    }

    result = await users_collection.insert_one(user_dict)

    return {
        "message": "User registered successfully",
        "user_id": str(result.inserted_id)
    }
