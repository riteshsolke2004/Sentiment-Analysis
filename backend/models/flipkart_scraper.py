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
        """Setup Chrome driver with optimal settings"""
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
        chrome_options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
        
        self.driver = webdriver.Chrome(options=chrome_options)
        self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        self.wait = WebDriverWait(self.driver, 20)
    
    def setup_session(self):
        """Setup requests session with headers"""
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        })
    
    def get_reviews_url(self, product_url):
        """Convert any Flipkart product URL to reviews URL"""
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
    
    def wait_for_reviews(self):
        """Wait for reviews to load properly"""
        try:
            self.wait.until(
                EC.presence_of_element_located(
                    (By.CSS_SELECTOR, "[data-testid='review'], div.col._2wzgFH, div._1AtVbE, div.col")
                )
            )
            # Scroll to load all content
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(3)
        except TimeoutException:
            print("Reviews not found on page")
    
    def get_review_containers(self):
        """Get all review containers using multiple selectors"""
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
        """Extract rating (keeping your working method)"""
        try:
            full_text = container.text
            lines = full_text.split('\n')
            
            # Look for single digit at the beginning
            for line in lines[:3]:
                line = line.strip()
                if line.isdigit() and 1 <= int(line) <= 5:
                    return line
            
            # Look for rating patterns
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
        """Extract location (keeping your working method)"""
        try:
            full_text = container.text
            
            # Look for "Certified Buyer" pattern
            pattern = r'Certified Buyer\s+([A-Za-z\s]+?)(?:\n|$)'
            match = re.search(pattern, full_text)
            if match:
                location = match.group(1).strip()
                location = re.sub(r'[^\w\s]', '', location)
                location = re.sub(r'\s+', ' ', location)
                return location
            
            # Alternative patterns
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
        """Enhanced date extraction with multiple strategies"""
        try:
            full_text = container.text
            
            # Strategy 1: Look for month + year patterns
            months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
            
            # Look for "Month YYYY" pattern
            for month in months:
                pattern = f'({month})\\s+(20\\d{{2}})'
                match = re.search(pattern, full_text)
                if match:
                    date = f"{match.group(1)} {match.group(2)}"
                    print(f"Found date: {date}")
                    return date
            
            # Strategy 2: Look for "Month, YYYY" pattern
            for month in months:
                pattern = f'({month}),\\s+(20\\d{{2}})'
                match = re.search(pattern, full_text)
                if match:
                    date = f"{match.group(1)} {match.group(2)}"
                    print(f"Found date: {date}")
                    return date
            
            # Strategy 3: Look in specific date elements
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
                            # Check if this text contains a date
                            for month in months:
                                if month in elem_text:
                                    year_match = re.search(r'20\d{2}', elem_text)
                                    if year_match:
                                        date = f"{month} {year_match.group()}"
                                        print(f"Found date in element: {date}")
                                        return date
                except Exception as e:
                    continue
            
            # Strategy 4: Look for lines that might contain dates
            lines = full_text.split('\n')
            for line in lines:
                line = line.strip()
                # Check if line contains month and year
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
        """Extract review title (keeping your working method)"""
        try:
            full_text = container.text
            
            # Look for common title patterns
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
        """Comprehensive name removal targeting specific patterns from your data"""
        if not review_text:
            return ""
        
        # Ultra-specific patterns based on your data
        specific_name_patterns = [
            # Names with initials like "Ajin V"
            r'\s+[A-Z][a-z]+\s+[A-Z]\s*$',
            
            # Names in parentheses like "Talim (sk)"
            r'\s+[A-Z][a-z]+\s*\([a-z]+\)\s*$',
            
            # Three-word names like "Mousam Guha Roy", "Sheetla Prasad Maurya"
            r'\s+[A-Z][a-z]+\s+[A-Z][a-z]+\s+[A-Z][a-z]+\s*$',
            
            # Three-word names like "Varsha Sadanand Salve"
            r'\s+[A-Z][a-z]+\s+[A-Z][a-z]+\s+[A-Z][a-z]+\s*$',
            
            # All caps three-word names like "ANUP SINGH GAUTAM"
            r'\s+[A-Z]{2,}\s+[A-Z]{2,}\s+[A-Z]{2,}\s*$',
            
            # Mixed case names
            r'\s+[A-Z][a-z]+\s+[A-Z]{2,}\s+[A-Z][a-z]+\s*$',
            
            # Standard two-word names
            r'\s+[A-Z][a-z]+\s+[A-Z][a-z]+\s*$',
            r'\s+[a-z]+\s+[a-z]+\s*$',
            r'\s+[A-Z]{2,}\s+[A-Z]{2,}\s*$',
            
            # Names with dates
            r'\s+[A-Z][a-z]+\s+[A-Z][a-z]+\s+(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s*$',
            r'\s+[A-Z][a-z]+\s+[A-Z][a-z]+\s+[A-Z][a-z]+\s+(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s*$',
            
            # Single names (be careful)
            r'\s+[A-Z][a-z]{4,}\s*$',
            r'\s+[A-Z]{5,}\s*$',
            
            # Customer patterns
            r'\s+[A-Z][a-z]+\s+Customer\s*$',
            r'\s+Customer\s*$',
            r'\s+Flipkart\s+Customer\s*$',
            
            # Time patterns
            r'\s+\d+\s*months?\s*ago\s*$',
            r'\s+\d+\s*days?\s*ago\s*$',
            r'\s+\d+\s*hours?\s*ago\s*$',
            
            # Date patterns
            r'\s+(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s+20\d{2}\s*$',
            r'\s+(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s*$',
            
            # Numbers
            r'\s+\d+\s*$',
        ]
        
        cleaned_text = review_text
        
        # Apply each pattern
        for pattern in specific_name_patterns:
            cleaned_text = re.sub(pattern, '', cleaned_text)
        
        # Remove trailing punctuation and spaces
        cleaned_text = re.sub(r'[,.\s]+$', '', cleaned_text)
        
        # Clean up extra spaces
        cleaned_text = re.sub(r'\s+', ' ', cleaned_text).strip()
        
        # Final validation - check if last 1-3 words are likely names
        words = cleaned_text.split()
        if len(words) > 1:
            # Check last 3 words
            for i in range(min(3, len(words))):
                last_words = words[-(i+1):]
                combined = ' '.join(last_words)
                
                # If it looks like a name pattern, remove it
                if (all(word[0].isupper() and word[1:].islower() for word in last_words if word.isalpha()) and 
                    len(combined) > 2 and 
                    combined not in ['Good', 'Nice', 'Great', 'Best', 'Super', 'Awesome', 'Perfect', 'Amazing', 'Excellent', 'Phone', 'Camera', 'Battery', 'Product', 'Quality', 'Performance', 'Display', 'Design', 'Experience', 'Service', 'Delivery', 'Apple', 'iPhone', 'Flipkart', 'Thanks', 'Thank', 'Love', 'Loved', 'Happy']):
                    cleaned_text = ' '.join(words[:-(i+1)])
                    break
        
        return cleaned_text
    
    def extract_review_text_clean(self, container):
        """Extract and clean review text from names and dates"""
        try:
            full_text = container.text
            lines = full_text.split('\n')
            
            # Skip rating, title, name, location, and date lines
            content_lines = []
            skip_patterns = [
                r'^\d$',  # Single digit (rating)
                r'Certified Buyer',
                r'^(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s+20\d{2}$',  # Full date
                r'^(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)$',  # Just month
                r'^\d+\s*helpful',  # Helpful votes
                r'^(Just wow!|Awesome|Excellent|Great product|Perfect product|Mind-blowing purchase|Worth every penny|Brilliant|Fabulous|Super|Must buy|Terrific|Wonderful|Classy product|Best in the market|Simply awesome|Highly recommended|Value-for-money|Good choice|Really Nice|Does the job|Terrific purchase|Worth the money|Nice|Mindblowing purchase|Valueformoney)$',  # Common titles
                r'^\d+\s*$',  # Just numbers
                r'^[A-Z][a-z]+\s+[A-Z][a-z]+\s*$',  # Two-word names
                r'^[A-Z][A-Z]+\s+[A-Z][A-Z]+\s*$',  # All caps names
                r'^[A-Z][a-z]+\s*$',  # Single names
                r'^Customer\s*$',  # Just "Customer"
                r'^Flipkart\s+Customer\s*$',  # "Flipkart Customer"
                r'^[A-Z][a-z]+\s+[A-Z][a-z]+\s+[A-Z][a-z]+\s*$',  # Three-word names
                r'^[A-Z]{2,}\s+[A-Z]{2,}\s+[A-Z]{2,}\s*$',  # All caps three-word names
            ]
            
            for line in lines:
                line = line.strip()
                if len(line) > 3:  # Only consider lines with some content
                    skip_line = False
                    for pattern in skip_patterns:
                        if re.match(pattern, line, re.IGNORECASE):
                            skip_line = True
                            break
                    
                    if not skip_line:
                        content_lines.append(line)
            
            if content_lines:
                review_text = ' '.join(content_lines)
                # Comprehensive cleaning for names
                cleaned_text = self.clean_review_text_comprehensive(review_text)
                
                # If after cleaning we have very short text, it might be invalid
                if len(cleaned_text) < 8:
                    return np.nan
                
                return cleaned_text if cleaned_text else np.nan
            
            return np.nan
            
        except Exception as e:
            return np.nan
    
    def scrape_reviews_from_page(self, page_url):
        """Scrape reviews from a single page with enhanced date extraction"""
        try:
            print(f"📄 Scraping: {page_url}")
            self.driver.get(page_url)
            
            # Wait for reviews to load
            self.wait_for_reviews()
            
            # Get review containers
            containers = self.get_review_containers()
            
            if not containers:
                print("No review containers found")
                return []
            
            reviews = []
            for i, container in enumerate(containers):
                try:
                    print(f"\n--- Processing container {i+1}/{len(containers)} ---")
                    
                    # Extract each field with enhanced date extraction
                    rating = self.extract_rating_properly(container)
                    location = self.extract_location_properly(container)
                    date = self.extract_date_enhanced(container)  # Enhanced date extraction
                    review_title = self.extract_review_title_properly(container)
                    
                    # Clean review text with comprehensive name removal
                    review_text = self.extract_review_text_clean(container)
                    
                    # Create review data
                    review_data = {
                        'rating': rating if rating else np.nan,
                        'review_title': review_title if review_title else np.nan,
                        'review_text': review_text,  # Can be NaN
                        'date': date if date else np.nan,
                        'location': location if location else np.nan
                    }
                    
                    # Check for duplicate
                    review_hash = self.create_review_hash(
                        str(review_data['review_text']),
                        str(review_data['review_title']),
                        str(review_data['rating'])
                    )
                    
                    if review_hash not in self.scraped_reviews:
                        self.scraped_reviews.add(review_hash)
                        reviews.append(review_data)
                        
                        # Show status
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
        """Create unique hash for duplicate detection"""
        content = f"{review_title}{review_text}{rating}".lower().strip()
        return hashlib.md5(content.encode()).hexdigest()
    
    def scrape_flipkart_reviews(self, product_url, max_pages=5):
        """Main scraping method"""
        try:
            print(f"🎯 Processing URL: {product_url}")
            
            # Get reviews URL
            reviews_url = self.get_reviews_url(product_url)
            if not reviews_url:
                print("❌ Could not determine reviews URL")
                return []
            
            print(f"📝 Reviews URL: {reviews_url}")
            
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
                
                # Random delay between pages
                time.sleep(random.uniform(3, 6))
            
            return all_reviews
            
        except Exception as e:
            print(f"❌ Error scraping reviews: {e}")
            return []
    
    def save_reviews(self, reviews, filename='perfect_flipkart_reviews.csv'):
        """Save reviews to CSV with dates and no names"""
        if not reviews:
            print("❌ No reviews to save")
            return
        
        # Create DataFrame
        df = pd.DataFrame(reviews)
        
        # Ensure columns are in correct order
        columns = ['rating', 'review_title', 'review_text', 'date', 'location']
        df = df[columns]
        
        # Save to CSV
        df.to_csv(filename, index=False, encoding='utf-8')
        
        print(f"✅ Saved {len(reviews)} reviews to {filename}")
        
        # Show statistics
        print(f"\n📊 Final Statistics:")
        print(f"Total reviews: {len(reviews)}")
        print(f"With ratings: {len([r for r in reviews if not pd.isna(r['rating'])])}")
        print(f"With dates: {len([r for r in reviews if not pd.isna(r['date'])])}")
        print(f"With locations: {len([r for r in reviews if not pd.isna(r['location'])])}")
        print(f"With valid review text: {len([r for r in reviews if not pd.isna(r['review_text'])])}")
        print(f"With NaN review text: {len([r for r in reviews if pd.isna(r['review_text'])])}")
        
        # Show sample reviews
        print(f"\n📋 Sample Perfect Reviews:")
        print(df.head())
    
    def close(self):
        """Close the driver"""
        if hasattr(self, 'driver'):
            self.driver.quit()


def main():
    scraper = FinalFlipkartScraper()
    
    try:
        # Get input from user
        product_url = input("Enter any Flipkart product URL: ").strip()
        
        if not product_url:
            print("❌ Please provide a valid Flipkart URL")
            return
        
        max_pages = int(input("Enter maximum pages to scrape (default: 3): ") or "3")
        filename = input("Enter output filename (default: perfect_flipkart_reviews.csv): ").strip()
        if not filename:
            filename = "perfect_flipkart_reviews.csv"
        
        print("\n🚀 Starting Flipkart scraper...")
        print("✅ Final fixes applied:")
        
        # Scrape reviews
        reviews = scraper.scrape_flipkart_reviews(product_url, max_pages)
        
        if reviews:
            # Save reviews
            scraper.save_reviews(reviews, filename)
            print("\n scraping completed!")
        else:
            print("❌ No reviews were extracted")
        
    except KeyboardInterrupt:
        print("\n⚠️  Scraping interrupted by user")
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        scraper.close()


if __name__ == "__main__":
    main()
