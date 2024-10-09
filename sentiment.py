import yfinance as yf
from transformers import pipeline
from goose3 import Goose
from requests import get
import pandas as pd
import os
from datetime import datetime

# Helper function to break long text into chunks for sentiment analysis
def chunk_text(text, chunk_size=512):
    return [text[i:i+chunk_size] for i in range(0, len(text), chunk_size)]

# Function to get sentiment of financial news within a date range
def get_sentiment(ticker, start_date=None, end_date=None):
    ticker_news = yf.Ticker(ticker)
    news_list = ticker_news.get_news()

    # Set up NLP pipeline
    extractor = Goose()
    pipe = pipeline("text-classification", model="ProsusAI/finbert")
    
    data = []
    positive, negative, neutral = 0, 0, 0

    for dic in news_list:
        title = dic['title']
        response = get(dic['link'])
        article = extractor.extract(raw_html=response.content)
        text = article.cleaned_text
        date = article.publish_date
        
        # Filter articles based on date range
        if start_date and date < start_date:
            continue
        if end_date and date > end_date:
            continue
        
        if len(text) > 512:
            chunks = chunk_text(text)
            sentiments = [pipe(chunk)[0]['label'] for chunk in chunks]
            sentiment = max(set(sentiments), key=sentiments.count)  # Get most frequent sentiment
        else:
            sentiment = pipe(text)[0]['label']
        
        data.append({'Date': date, 'Article title': title, 'Article sentiment': sentiment})
        
        if sentiment == 'positive':
            positive += 1
        elif sentiment == 'negative':
            negative += 1
        elif sentiment == 'neutral':
            neutral += 1

    df = pd.DataFrame(data)
    print(f"Sentiment Summary for {ticker}: {positive} positive, {negative} negative, {neutral} neutral")
    return df

# Function to save sentiment analysis to CSV
def save_sentiment_to_csv(ticker, start_date=None, end_date=None):
    df = get_sentiment(ticker, start_date, end_date)
    if not os.path.exists('out'):
        os.makedirs('out')
    df.to_csv(f'out/{ticker}_sentiment.csv', index=False)
