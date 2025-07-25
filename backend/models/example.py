from flipkart_scraper import scrape_and_save
from sentiment_analyser import SentimentModel
from summarizer import summarize_reviews


sentiment = SentimentModel()
# product_url = "https://www.flipkart.com/redmi-note-14-pro-5g-phantom-purple-128-gb/p/itm260f3edcb0cde?pid=MOBH753HNZXZKTEG&lid=LSTMOBH753HNZXZKTEGBPREXI&marketplace=FLIPKART&cmpid=content_mobile_22428124232_x_8965229628_gmc_pla&tgi=sem,1,G,11214002,x,,,,,,,m,,mobile,,,,,&entryMethod=22428124232&cmpid=content_22428124232_gmc_pla&gad_source=1&gad_campaignid=22428139664&gclid=CjwKCAjw4K3DBhBqEiwAYtG_9CUaV3A2vOOZwHypi8UVz2kfvqfZsooopSj_1_LCml7VDPXaDZjVVhoC_g0QAvD_BwE"
# scrape_and_save(product_url, max_pages=10)
# sbc = sentiment.annotate_sentiments(input_csv='./data/reviews.csv', output_csv='./data/reviews_labeled.csv')
postive_reviews, negative_reviews = summarize_reviews('./data/reviews_labeled.csv')
print("positive:", postive_reviews)
print("negative:", negative_reviews)