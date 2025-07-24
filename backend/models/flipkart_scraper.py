import requests
from bs4 import BeautifulSoup
import pandas as pd
import numpy as np
import time
import random
import re
from urllib.parse import urljoin, urlparse
import hashlib
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException

class FinalFlipkartScraper:
    def __init__(self):
        self.setup_driver()
        self.scraped_reviews = set()
        self.session = requests.Session()
        self.setup_session()
    
    def setup_driver(self):
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        chrome_options.add_argument("--disable-extensions")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--window-size=1920,1080")
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option('useAutomationExtension', False)
        chrome_options.add_argument(
            "--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        self.driver = webdriver.Chrome(options=chrome_options)
        self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        self.wait = WebDriverWait(self.driver, 20)
    
    def setup_session(self):
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        })

    def get_reviews_url(self, product_url):
        try:
            if '/product-reviews/' in product_url:
                return product_url
            elif '/p/' in product_url:
                product_id = product_url.split('/p/')[1].split('?')[0]
                base_url = product_url.split('/p/')[0]
                reviews_url = f"{base_url}/product-reviews/{product_id}"
                return reviews_url
            elif '/dp/' in product_url:
                product_id = product_url.split('/dp/')[1].split('?')[0]
                base_url = product_url.split('/dp/')[0]
                reviews_url = f"{base_url}/product-reviews/{product_id}"
                return reviews_url
            else:
                self.driver.get(product_url)
                time.sleep(3)
                review_links = self.driver.find_elements(By.XPATH, "//a[contains(@href, 'product-reviews') or contains(text(), 'Reviews') or contains(text(), 'reviews')]")
                if review_links:
                    href = review_links[0].get_attribute('href')
                    if href:
                        return href
                return None
        except Exception as e:
            print(f"Error getting reviews URL: {e}")
            return None

    ############
    # NEW: Detect max number of review pages automatically
    ############
    def get_max_review_pages(self, reviews_url):
        """Detect total number of review pages from the reviews page pagination."""
        try:
            self.driver.get(reviews_url)
            self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "div._2MImiq")))
            time.sleep(1)  # Small pause for rendering

            # Standard Flipkart "Page 1 of XX" selector
            els = self.driver.find_elements(By.CSS_SELECTOR, "div._2MImiq span")
            for el in els:
                text = el.text.strip()
                if "Page" in text and "of" in text:
                    m = re.search(r'of\s+(\d+)', text)
                    if m:
                        return int(m.group(1))
            # Alternate: Look for numbered pagination buttons if above fails
            page_btns = self.driver.find_elements(By.CSS_SELECTOR, "nav .yFHi8N")
            if page_btns:
                nums = []
                for btn in page_btns:
                    txt = btn.text.strip()
                    if txt.isdigit():
                        nums.append(int(txt))
                if nums:
                    return max(nums)
        except Exception as e:
            print(f"Could not determine max review pages: {e}")
        return 1

    def wait_for_reviews(self):
        try:
            self.wait.until(
                EC.presence_of_element_located(
                    (By.CSS_SELECTOR, "[data-testid='review'], div.col._2wzgFH, div._1AtVbE, div.col")
                )
            )
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(3)
        except TimeoutException:
            print("Reviews not found on page")

    def get_review_containers(self):
        selectors = [
            "[data-testid='review']",
            "div.col._2wzgFH",
            "div._1AtVbE",
            "div.col",
            "div[class*='K0kLPL']"
        ]
        for selector in selectors:
            containers = self.driver.find_elements(By.CSS_SELECTOR, selector)
            if containers and len(containers) > 1:
                print(f"Found {len(containers)} review containers using: {selector}")
                return containers
        return []

    def extract_rating_properly(self, container):
        try:
            full_text = container.text
            lines = full_text.split('\n')
            for line in lines[:3]:
                line = line.strip()
                if line.isdigit() and 1 <= int(line) <= 5:
                    return line
            rating_patterns = [
                r'^(\d)\s*$',
                r'(\d)\s*★',
                r'(\d)\s*star',
                r'(\d)\s*out\s*of\s*5'
            ]
            for pattern in rating_patterns:
                match = re.search(pattern, full_text, re.MULTILINE)
                if match:
                    rating = int(match.group(1))
                    if 1 <= rating <= 5:
                        return str(rating)
            return ""
        except Exception as e:
            return ""

    def extract_location_properly(self, container):
        try:
            full_text = container.text
            pattern = r'Certified Buyer\s+([A-Za-z\s]+?)(?:\n|$)'
            match = re.search(pattern, full_text)
            if match:
                location = match.group(1).strip()
                location = re.sub(r'[^\w\s]', '', location)
                location = re.sub(r'\s+', ' ', location)
                return location
            lines = full_text.split('\n')
            for line in lines:
                if 'Certified Buyer' in line:
                    parts = line.split('Certified Buyer')
                    if len(parts) > 1:
                        location = parts[1].strip()
                        location = re.sub(r'[^\w\s]', '', location)
                        location = re.sub(r'\s+', ' ', location)
                        if location and len(location) > 2:
                            return location
            return ""
        except Exception as e:
            return ""

    def extract_date_enhanced(self, container):
        try:
            full_text = container.text
            months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
            for month in months:
                pattern = f'({month})\\s+(20\\d{{2}})'
                match = re.search(pattern, full_text)
                if match:
                    date = f"{match.group(1)} {match.group(2)}"
                    print(f"Found date: {date}")
                    return date
            for month in months:
                pattern = f'({month}),\\s+(20\\d{{2}})'
                match = re.search(pattern, full_text)
                if match:
                    date = f"{match.group(1)} {match.group(2)}"
                    print(f"Found date: {date}")
                    return date
            date_selectors = [
                "span[class*='date']",
                "div[class*='date']",
                "span[class*='time']",
                "div[class*='time']",
                "span._2sc7ZR",
                "div._2sc7ZR",
                "span[class*='_2sc7ZR']",
                "div[class*='_2sc7ZR']"
            ]
            for selector in date_selectors:
                try:
                    date_elements = container.find_elements(By.CSS_SELECTOR, selector)
                    for elem in date_elements:
                        elem_text = elem.text.strip()
                        if elem_text:
                            for month in months:
                                if month in elem_text:
                                    year_match = re.search(r'20\d{2}', elem_text)
                                    if year_match:
                                        date = f"{month} {year_match.group()}"
                                        print(f"Found date in element: {date}")
                                        return date
                except Exception as e:
                    continue
            lines = full_text.split('\n')
            for line in lines:
                line = line.strip()
                for month in months:
                    if month in line:
                        year_match = re.search(r'20\d{2}', line)
                        if year_match:
                            date = f"{month} {year_match.group()}"
                            print(f"Found date in line: {date}")
                            return date
            print("No date found")
            return ""
        except Exception as e:
            print(f"Error extracting date: {e}")
            return ""

    def extract_review_title_properly(self, container):
        try:
            full_text = container.text
            title_patterns = [
                r'(Just wow!|Awesome|Excellent|Great product|Perfect product|Mind-blowing purchase|Worth every penny|Brilliant|Fabulous|Super|Must buy|Terrific|Wonderful|Classy product|Best in the market|Simply awesome|Highly recommended|Value-for-money|Good choice|Really Nice|Does the job|Terrific purchase|Worth the money|Nice|Mindblowing purchase|Valueformoney)'
            ]
            for pattern in title_patterns:
                match = re.search(pattern, full_text, re.IGNORECASE)
                if match:
                    return match.group(1)
            return ""
        except Exception as e:
            return ""

    def clean_review_text_comprehensive(self, review_text):
        if not review_text:
            return ""
        specific_name_patterns = [
            r'\s+[A-Z][a-z]+\s+[A-Z]\s*$',
            r'\s+[A-Z][a-z]+\s*\([a-z]+\)\s*$',
            r'\s+[A-Z][a-z]+\s+[A-Z][a-z]+\s+[A-Z][a-z]+\s*$',
            r'\s+[A-Z][a-z]+\s+[A-Z][a-z]+\s+[A-Z][a-z]+\s*$',
            r'\s+[A-Z]{2,}\s+[A-Z]{2,}\s+[A-Z]{2,}\s*$',
            r'\s+[A-Z][a-z]+\s+[A-Z]{2,}\s+[A-Z][a-z]+\s*$',
            r'\s+[A-Z][a-z]+\s+[A-Z][a-z]+\s*$',
            r'\s+[a-z]+\s+[a-z]+\s*$',
            r'\s+[A-Z]{2,}\s+[A-Z]{2,}\s*$',
            r'\s+[A-Z][a-z]+\s+[A-Z][a-z]+\s+(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s*$',
            r'\s+[A-Z][a-z]+\s+[A-Z][a-z]+\s+[A-Z][a-z]+\s+(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s*$',
            r'\s+[A-Z][a-z]{4,}\s*$',
            r'\s+[A-Z]{5,}\s*$',
            r'\s+[A-Z][a-z]+\s+Customer\s*$',
            r'\s+Customer\s*$',
            r'\s+Flipkart\s+Customer\s*$',
            r'\s+\d+\s*months?\s*ago\s*$',
            r'\s+\d+\s*days?\s*ago\s*$',
            r'\s+\d+\s*hours?\s*ago\s*$',
            r'\s+(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s+20\d{2}\s*$',
            r'\s+(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s*$',
            r'\s+\d+\s*$',
        ]
        cleaned_text = review_text
        for pattern in specific_name_patterns:
            cleaned_text = re.sub(pattern, '', cleaned_text)
        cleaned_text = re.sub(r'[,.\s]+$', '', cleaned_text)
        cleaned_text = re.sub(r'\s+', ' ', cleaned_text).strip()
        words = cleaned_text.split()
        if len(words) > 1:
            for i in range(min(3, len(words))):
                last_words = words[-(i+1):]
                combined = ' '.join(last_words)
                if (
                    all(word[0].isupper() and word[1:].islower() for word in last_words if word.isalpha()) and
                    len(combined) > 2 and
                    combined not in [
                        'Good', 'Nice', 'Great', 'Best', 'Super', 'Awesome', 'Perfect', 'Amazing', 'Excellent',
                        'Phone', 'Camera', 'Battery', 'Product', 'Quality', 'Performance', 'Display', 'Design',
                        'Experience', 'Service', 'Delivery', 'Apple', 'iPhone', 'Flipkart', 'Thanks', 'Thank', 'Love',
                        'Loved', 'Happy'
                    ]
                ):
                    cleaned_text = ' '.join(words[:-(i+1)])
                    break
        return cleaned_text

    def extract_review_text_clean(self, container):
        try:
            full_text = container.text
            lines = full_text.split('\n')
            content_lines = []
            skip_patterns = [
                r'^\d$',
                r'Certified Buyer',
                r'^(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s+20\d{2}$',
                r'^(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)$',
                r'^\d+\s*helpful',
                r'^(Just wow!|Awesome|Excellent|Great product|Perfect product|Mind-blowing purchase|Worth every penny|Brilliant|Fabulous|Super|Must buy|Terrific|Wonderful|Classy product|Best in the market|Simply awesome|Highly recommended|Value-for-money|Good choice|Really Nice|Does the job|Terrific purchase|Worth the money|Nice|Mindblowing purchase|Valueformoney)$',
                r'^\d+\s*$',
                r'^[A-Z][a-z]+\s+[A-Z][a-z]+\s*$',
                r'^[A-Z][A-Z]+\s+[A-Z][A-Z]+\s*$',
                r'^[A-Z][a-z]+\s*$',
                r'^Customer\s*$',
                r'^Flipkart\s+Customer\s*$',
                r'^[A-Z][a-z]+\s+[A-Z][a-z]+\s+[A-Z][a-z]+\s*$',
                r'^[A-Z]{2,}\s+[A-Z]{2,}\s+[A-Z]{2,}\s*$',
            ]
            for line in lines:
                line = line.strip()
                if len(line) > 3:
                    skip_line = False
                    for pattern in skip_patterns:
                        if re.match(pattern, line, re.IGNORECASE):
                            skip_line = True
                            break
                    if not skip_line:
                        content_lines.append(line)
            if content_lines:
                review_text = ' '.join(content_lines)
                cleaned_text = self.clean_review_text_comprehensive(review_text)
                if len(cleaned_text) < 8:
                    return np.nan
                return cleaned_text if cleaned_text else np.nan
            return np.nan
        except Exception as e:
            return np.nan

    def scrape_reviews_from_page(self, page_url):
        try:
            print(f"📄 Scraping: {page_url}")
            self.driver.get(page_url)
            self.wait_for_reviews()
            containers = self.get_review_containers()
            if not containers:
                print("No review containers found")
                return []
            reviews = []
            for i, container in enumerate(containers):
                try:
                    print(f"\n--- Processing container {i+1}/{len(containers)} ---")
                    rating = self.extract_rating_properly(container)
                    location = self.extract_location_properly(container)
                    date = self.extract_date_enhanced(container)
                    review_title = self.extract_review_title_properly(container)
                    review_text = self.extract_review_text_clean(container)
                    review_data = {
                        'rating': rating if rating else np.nan,
                        'review_title': review_title if review_title else np.nan,
                        'review_text': review_text,
                        'date': date if date else np.nan,
                        'location': location if location else np.nan
                    }
                    review_hash = self.create_review_hash(
                        str(review_data['review_text']),
                        str(review_data['review_title']),
                        str(review_data['rating'])
                    )
                    if review_hash not in self.scraped_reviews:
                        self.scraped_reviews.add(review_hash)
                        reviews.append(review_data)
                        print(f"✅ Added review: Rating={rating}, Date={date}, Text='{str(review_text)[:50] if not pd.isna(review_text) else 'NaN'}...'")
                    else:
                        print(f"⚠️ Duplicate review - skipped")
                except Exception as e:
                    print(f"Error processing container {i}: {e}")
                    continue
            return reviews
        except Exception as e:
            print(f"Error scraping page: {e}")
            return []

    def create_review_hash(self, review_text, review_title, rating):
        content = f"{review_title}{review_text}{rating}".lower().strip()
        return hashlib.md5(content.encode()).hexdigest()

    #########################
    # MAIN SCRAPING METHOD
    #########################
    def scrape_flipkart_reviews(self, product_url, max_pages=None):
        """
        Main scraping method:
        - If max_pages is None, automatically detect and scrape all available review pages.
        """
        try:
            print(f"🎯 Processing URL: {product_url}")
            reviews_url = self.get_reviews_url(product_url)
            if not reviews_url:
                print("❌ Could not determine reviews URL")
                return []
            print(f"📝 Reviews URL: {reviews_url}")
            # AUTO-DETECT max number of pages if not specified
            if max_pages is None:
                max_pages = self.get_max_review_pages(reviews_url)
                print(f"Detected {max_pages} review pages.")
            all_reviews = []
            for page_num in range(1, max_pages + 1):
                if '?' in reviews_url:
                    page_url = f"{reviews_url}&page={page_num}"
                else:
                    page_url = f"{reviews_url}?page={page_num}"
                page_reviews = self.scrape_reviews_from_page(page_url)
                if not page_reviews:
                    print(f"No reviews found on page {page_num}")
                    if page_num == 1:
                        continue
                    else:
                        break
                all_reviews.extend(page_reviews)
                print(f"✅ Found {len(page_reviews)} reviews on page {page_num}")
                time.sleep(random.uniform(3, 6))
            return all_reviews
        except Exception as e:
            print(f"❌ Error scraping reviews: {e}")
            return []

    def save_reviews(self, reviews, filename='perfect_flipkart_reviews.csv'):
        if not reviews:
            print("❌ No reviews to save")
            return
        df = pd.DataFrame(reviews)
        columns = ['rating', 'review_title', 'review_text', 'date', 'location']
        df = df[columns]
        df.to_csv(filename, index=False, encoding='utf-8')
        print(f"✅ Saved {len(reviews)} reviews to {filename}")
        print(f"\n📊 Final Statistics:")
        print(f"Total reviews: {len(reviews)}")
        print(f"With ratings: {len([r for r in reviews if not pd.isna(r['rating'])])}")
        print(f"With dates: {len([r for r in reviews if not pd.isna(r['date'])])}")
        print(f"With locations: {len([r for r in reviews if not pd.isna(r['location'])])}")
        print(f"With valid review text: {len([r for r in reviews if not pd.isna(r['review_text'])])}")
        print(f"With NaN review text: {len([r for r in reviews if pd.isna(r['review_text'])])}")
        print(f"\n📋 Sample Perfect Reviews:")
        print(df.head())

    def close(self):
        if hasattr(self, 'driver'):
            self.driver.quit()

#############################
# UTILITY FUNCTION
#############################

def scrape_and_save(product_url, max_pages=None, filename='reviews.csv'):
    """
    Scrape reviews from Flipkart and save as 'reviews.csv'.
    By default, scrapes ALL available review pages.
    """
    scraper = FinalFlipkartScraper()
    try:
        print("\n🚀 Starting Flipkart scraper...")
        reviews = scraper.scrape_flipkart_reviews(product_url, max_pages)
        if reviews:
            scraper.save_reviews(reviews, filename)
            print(f"\nScraping completed! Saved to {filename}")
        else:
            print("❌ No reviews were extracted")
    finally:
        scraper.close()

