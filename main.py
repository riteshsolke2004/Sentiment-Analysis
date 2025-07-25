from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import pandas as pd
import numpy as np

# --- Correctly import the scraper CLASS and the sentiment analyzer INSTANCE ---
from models.flipkart_scraper import FinalFlipkartScraper
from models.sentiment_model import sentiment_analyzer

# --- Assuming you still need these routers for your full application ---
from dashboard import router as dashboard_router
from routes.signup import router as signup_router
from routes.login import router as login_router

app = FastAPI()

# --- Load the AI Model on Application Startup for efficiency ---
@app.on_event("startup")
async def startup_event():
    """Load the sentiment analysis model when the server starts."""
    sentiment_analyzer.load()

# --- CORS Middleware to allow communication with your frontend ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8080", "http://localhost:3000", "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Include other parts of your application ---
app.include_router(dashboard_router)
app.include_router(signup_router)
app.include_router(login_router)

# --- Pydantic Models for request data validation ---
class TextData(BaseModel):
    text: str

class ScrapeRequest(BaseModel):
    url: str
    max_pages: int = None

# --- API Endpoints ---

@app.post("/analyze")
def analyze(data: TextData):
    """
    Performs sentiment analysis on the provided text using the loaded RoBERTa model.
    """
    if not data.text or not data.text.strip():
        raise HTTPException(status_code=400, detail="Text for analysis cannot be empty.")

    try:
        # Get the prediction from the sentiment model
        result = sentiment_analyzer.predict(data.text)

        # Add 'score' and 'keywords' to match frontend expectations
        result["score"] = int(result["confidence"])
        result["keywords"] = []  # You can add a real keyword extractor here later

        return result
    except Exception as e:
        print(f"❌ Error during analysis: {e}")
        raise HTTPException(status_code=500, detail="Failed to analyze sentiment.")


@app.post("/scrape")
def scrape_reviews_endpoint(request: ScrapeRequest):
    """
    Endpoint to scrape reviews from a Flipkart URL and return them as JSON.
    """
    scraper = FinalFlipkartScraper()
    try:
        print(f"🚀 Starting scraper for URL: {request.url}")
        
        # Call the method that returns a list of reviews
        reviews_list = scraper.scrape_flipkart_reviews(request.url, request.max_pages)

        if not reviews_list:
            raise HTTPException(status_code=404, detail="No reviews were found. Check the URL or the website structure.")

        # Convert list of dictionaries to a DataFrame for easy cleaning
        df = pd.DataFrame(reviews_list)
        
        # Replace numpy's NaN with None for proper JSON conversion
        df = df.replace({pd.NA: None, np.nan: None})

        # Convert the cleaned DataFrame back to a list of dictionaries
        reviews_json = df.to_dict(orient='records')
        
        print(f"✅ Scraping successful. Returning {len(reviews_json)} reviews.")
        return {"reviews": reviews_json}

    except Exception as e:
        print(f"❌ An error occurred during scraping: {e}")
        raise HTTPException(status_code=500, detail=str(e))

    finally:
        # CRUCIAL: Always close the scraper to free up resources
        print("Closing scraper resources...")
        scraper.close()