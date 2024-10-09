from finvizfinance.screener import Overview
import pandas as pd 
import csv 
import os

# Function to find a list of undervalued stocks or growth stocks based on strategy
def get_undervalued_stocks(strategy):

    foverview = Overview()
    
    if strategy == 'value':
        filters_dict = {'Debt/Equity': 'Under 1',
                        'PEG': 'Low (<1)',
                        'Operating Margin': 'Positive (>0%)',
                        'P/B': 'Low (<1)',
                        'P/E': 'Low (<15)',
                        'InsiderTransactions': 'Positive (>0%)'}
    #this needs to be checked for proper growth strategy code
    elif strategy == 'growth':
        filters_dict = {'Debt/Equity': 'Under 1',
                        'PEG': 'High (>2)',
                        'EPS growthqtr over qtr': 'Positive (>0%)',
                        'EPS growthnext 5 years': 'High (>25%)',
                        'Return on Equity': 'Over +15%'}

    # Apply the filters and retrieve stock data
    foverview.set_filter(filters_dict=filters_dict)
    df_overview = foverview.screener_view()

    if not os.path.exists('out'):
        os.makedirs('out')
    
    df_overview.to_csv(f'out/{strategy}_Overview.csv', index=False)
    tickers = df_overview['Ticker'].to_list()
    
    print(f"Stocks found using the {strategy} strategy: {len(tickers)}")
    return tickers
