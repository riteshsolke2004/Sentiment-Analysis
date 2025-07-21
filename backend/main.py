from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import random
from dashboard import router as dashboard_router
from routes.signup import router as signup_router
from routes.login import router as login_router

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8080"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(dashboard_router)
app.include_router(signup_router)
app.include_router(login_router)
class TextData(BaseModel):
    text: str


@app.post("/analyze")
def analyze(data: TextData):
    text = data.text.lower()
    positive_keywords = ["amazing", "great", "fantastic", "love"]
    negative_keywords = ["bad", "poor", "hate", "terrible"]
    score = random.randint(40, 90)
    confidence = random.uniform(80, 99)
    sentiment = "Neutral"

    if any(word in text for word in positive_keywords):
        sentiment = "Positive"
    elif any(word in text for word in negative_keywords):
        sentiment = "Negative"

    return {
        "sentiment": sentiment,
        "score": score,
        "confidence": confidence,
        "keywords": [word for word in text.split() if word in positive_keywords + negative_keywords]
    }
