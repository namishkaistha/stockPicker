import screening
from finvizfinance.screener import Overview
import pandas as pd 
import csv 
import os
from transformers import pipeline
import yfinance as yf
from goose3 import Goose
from requests import get 
from datetime import datetime, timedelta
import holidays
from concurrent.futures import ThreadPoolExecutor, as_completed

# Check if yesterday was a trading day
def get_last_trading_day():
    today = datetime.now()
    us_holidays = holidays.US()  # Get US holidays
    yesterday = today - timedelta(days=1)
    
    # Skip weekends and holidays
    while yesterday.weekday() > 4 or yesterday in us_holidays:
        yesterday -= timedelta(days=1)
    
    return yesterday.strftime('%Y-%m-%d')

# Improved turtle_trading function
def turtle_trading(stock):
    try:
        # Fetch historical data for the stock
        yesterday_str = get_last_trading_day()
        data = yf.download(stock, start='2022-01-01', end=yesterday_str)
        
        if data.empty:
            print(f"No data found for {stock}.")
            return pd.DataFrame()
        
        # Calculate indicators
        data['20D_High'] = data['High'].rolling(window=20).max()
        data['20D_Low'] = data['Low'].rolling(window=20).min()
        data['50D_SMA'] = data['Close'].rolling(window=50).mean()
        data['High-Low'] = data['High'] - data['Low']
        data['High-PrevClose'] = abs(data['High'] - data['Close'].shift(1))
        data['Low-PrevClose'] = abs(data['Low'] - data['Close'].shift(1))
        data['TrueRange'] = data[['High-Low', 'High-PrevClose', 'Low-PrevClose']].max(axis=1)
        data['ATR'] = data['TrueRange'].rolling(window=20).mean()

        # Generate signals
        data['Buy_Signal'] = (data['Close'] > data['20D_High'])
        data['Sell_Signal'] = (data['Close'] < data['20D_Low'])
        
        # Initialize position tracking
        data['Position'] = 0
        data.loc[data['Buy_Signal'], 'Position'] = 1
        data.loc[data['Sell_Signal'], 'Position'] = -1
        
        # Calculate daily returns and cumulative returns
        data['Daily_Return'] = data['Position'].shift(1) * data['Close'].pct_change()
        data['Cumulative_Return'] = (1 + data['Daily_Return']).cumprod()
    
        return data
    except Exception as e:
        print(f"Error fetching data for {stock}: {e}")
        return pd.DataFrame()

def analyze_stock(ticker):
    print(f"Running Turtle Trading for {ticker}...")
    trading_data = turtle_trading(ticker)

    if trading_data.empty:
        print(f"No trading data available for {ticker}.")
        return
    
    latest_data = trading_data.iloc[-1]
    
    if latest_data['Buy_Signal']:
        signal = 'BUY'
    elif latest_data['Sell_Signal']:
        signal = 'SELL'
    else:
        signal = 'HOLD'
    
    print(f"Signal for {ticker}: {signal}")
    print(f"Cumulative Return: {latest_data['Cumulative_Return']:.2f}")
    print(f"Closing Price: {latest_data['Close']:.2f}")
    print(f"20-Day High: {latest_data['20D_High']:.2f}")
    print(f"20-Day Low: {latest_data['20D_Low']:.2f}")

def analyze_stocks_in_parallel(tickers):
    results = {}

    # ThreadPoolExecutor allows parallel execution of stock analysis
    with ThreadPoolExecutor(max_workers=8) as executor:  # Adjust max_workers based on system capabilities
        futures = {executor.submit(analyze_stock, ticker): ticker for ticker in tickers}
        
        # As each future completes, store the result
        for future in as_completed(futures):
            ticker = futures[future]
            try:
                results[ticker] = future.result()  # Store the result for each ticker
            except Exception as e:
                print(f"Error analyzing {ticker}: {e}")
    
    # Now, after all analysis is completed, print the results
    print("\nAll stock analyses complete. Here are the results:")
    for ticker, result in results.items():
        print(f"Ticker: {ticker}, Analysis Result: {result}")
    
    return results



# Function to save turtle trading data to CSV
def save_turtle_trading_to_csv(ticker):
    df = turtle_trading(ticker)
    if df.empty:
        print(f"Skipping saving for {ticker} due to missing data.")
        return
    if not os.path.exists('out'):
        os.makedirs('out')
    df.to_csv(f'out/{ticker}_turtle_trading.csv', index=False)


