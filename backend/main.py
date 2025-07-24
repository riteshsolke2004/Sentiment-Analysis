from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import random
from dashboard import router as dashboard_router
from routes.signup import router as signup_router
from routes.login import router as login_router
from models.flipkart_scraper import scrape_and_save
from models.sentiment_analyser import annotate_sentiments
from models.summarizer import summarize_reviews

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
def analyze(product_url):
    scrape_and_save(product_url, max_pages=80, filename='reviews.csv')
    annotate_sentiments('reviews.csv', 'reviews_labeled.csv')
    summarize_reviews('reviews_labeled.csv')