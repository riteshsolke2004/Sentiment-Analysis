from flipkart_scraper import scrape_and_save
from sentiment_analyser import annotate_sentiments
from summarizer import summarize_reviews

product_url = "https://www.flipkart.com/apple-iphone-11-black-128-gb/p/itm8244e8d955aba?pid=MOBFWQ6BKRYBP5X8&lid=LSTMOBFWQ6BKRYBP5X8IBG6BS&marketplace=FLIPKART&cmpid=content_mobile_8965229628_gmc"
scrape_and_save(product_url, max_pages=80, filename='reviews.csv')
annotate_sentiments('reviews.csv', 'reviews_labeled.csv')
postive_reviews, negative_reviews = summarize_reviews('reviews_labeled.csv')
