from fastapi import APIRouter, HTTPException
from motor.motor_asyncio import AsyncIOMotorClient
from pydantic import BaseModel
from datetime import datetime
from bson import ObjectId

router = APIRouter()

# MongoDB setup
client = AsyncIOMotorClient("mongodb://localhost:27017")
db = client["sentimentDB"]
collection = db["reviews"]

# Review submission model
class ReviewData(BaseModel):
    text: str
    sentiment: str  # 'Positive', 'Neutral', 'Negative'
    score: int      # e.g., 85
    confidence: float  # e.g., 0.92

@router.post("/api/submit-review")
async def submit_review(data: ReviewData):
    review_doc = {
        "text": data.text,
        "sentiment": data.sentiment,
        "score": data.score,
        "confidence": data.confidence,
        "timestamp": datetime.utcnow()
    }
    result = await collection.insert_one(review_doc)
    return {"message": "Review stored", "id": str(result.inserted_id)}


# ✅ GET: fetch recent reviews for dashboard
@router.get("/get-reviews")
async def get_reviews():
    try:
        reviews = []
        async for review in collection.find().sort("timestamp", -1).limit(5):
            reviews.append({
                "id": str(review["_id"]),
                "text": review["text"],
                "sentiment": review["sentiment"],
                "score": review["score"]
            })
        return reviews
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
