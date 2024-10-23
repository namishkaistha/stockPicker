import screening
import turtleTrading
import sentiment
import os
import json

# File to store user portfolios
PORTFOLIO_FILE = 'portfolios.json'

def load_portfolios():
    """Load portfolios from a file,  handle empty or invalid JSON."""
    if os.path.exists(PORTFOLIO_FILE):
        try:
            with open(PORTFOLIO_FILE, 'r') as file:
                return json.load(file)
        except json.JSONDecodeError:
            print(f"Warning: {PORTFOLIO_FILE} is empty or contains invalid JSON. Starting with an empty portfolio.")
            return {}
    return {}


def save_portfolios(portfolios):
    """Save portfolios to a file."""
    with open(PORTFOLIO_FILE, 'w') as file:
        json.dump(portfolios, file, indent=4)

def create_or_add_portfolio(portfolios, username, action):
    """Create a new portfolio or add stocks to an existing one."""
    if username in portfolios and action == 'create':
        print("Portfolio already exists. This will add to the existing portfolio")

    if username not in portfolios:
        portfolios[username] = []

    add_more = 'y'
    while add_more == 'y':
        strategy = select_strategy()
        tickers = screening.get_undervalued_stocks(strategy)

        print(f"Stocks available for {strategy} strategy: {tickers}")
        stock_choice = select_ticker(tickers)

        # Check for duplicate before performing analysis
        perform_analysis(stock_choice, tickers)
        addition = input(f"Would you like to add {stock_choice} to your portfolio? (y/n): ").lower()
        if addition == 'y':
            if stock_choice in portfolios[username]:
                print(f"{stock_choice} is already in your portfolio.")
                add_more = input("Would you like to add another stock? (y/n): ").lower()
            else:
                portfolios[username].append(stock_choice)
                print(f"{stock_choice} has been added to your portfolio.")
                add_more = input("Would you like to add another stock? (y/n): ").lower()
        elif addition == 'n':
            add_more = input("Would you like to add another stock? (y/n): ").lower()

        else:
            print("Invalid input. Please try again.")

    save_portfolios(portfolios)
    print(f"Portfolio for {username} updated.")

def view_portfolio(portfolios, username):
    """View an existing portfolio and display signals for each stock."""
    if username not in portfolios or len(portfolios[username]) == 0:
        print(f"No portfolio found for {username}.")
        return

    print(f"Stocks in {username}'s portfolio: {portfolios[username]}")
    for stock in portfolios[username]:
        turtleTrading.analyze_stock(stock)

# Existing stock analysis and workflow functions
def select_strategy():
    """Allow the user to choose between Value and Growth investing strategy."""
    while True:
        strategy = input("Choose your investing strategy - 'v' for Value, 'g' for Growth: ").lower()
        if strategy == 'v':
            print("You've chosen the Value investing strategy.")
            return 'value'
        elif strategy == 'g':
            print("You've chosen the Growth investing strategy.")
            return 'growth'
        else:
            print("Invalid choice. Please enter 'v' for Value or 'g' for Growth.")

def select_ticker(tickers):
    """Allow the user to select a ticker or analyze all."""
    while True:
        stock_choice = input("Enter the ticker symbol you'd like to analyze ").upper()
        if stock_choice == 'ALL':
            return 'ALL'
        elif stock_choice in tickers:
            return stock_choice
        else:
            print("Invalid ticker. Please try again.")

def show_more_options():
    """Prompt user to see more about the stock after analysis."""
    while True:
        choice = input("Would you like to see more about this stock (sentiment analysis and detailed data)? Type 'yes' or 'no': ").lower()
        if choice in ['yes', 'no']:
            return choice == 'yes'
        else:
            print("Invalid choice. Please enter 'yes' or 'no'.")

def perform_analysis(ticker, tickers):
    """Run Turtle Trading analysis and optionally perform sentiment analysis."""
    if ticker == 'ALL':
        turtleTrading.analyze_stocks_in_parallel(tickers)  # Concurrent analysis
        for stock in tickers:
            turtleTrading.analyze_stock(stock)
            if show_more_options():
                start_date, end_date = select_sentiment_dates()
                sentiment.save_sentiment_to_csv(stock, start_date, end_date)
    else:
        turtleTrading.analyze_stock(ticker)
        if show_more_options():
            start_date, end_date = select_sentiment_dates()
            sentiment.save_sentiment_to_csv(ticker, start_date, end_date)

def continue_or_exit():
    """Prompt the user to continue with another analysis or exit the program."""
    while True:
        next_action = input("Would you like to analyze another stock? Type 'stock' to continue or 'exit' to quit: ").lower()
        if next_action == 'stock':
            return True
        elif next_action == 'exit':
            print("Exiting the program. Goodbye!")
            return False
        else:
            print("Invalid choice. Please enter 'stock' or 'exit'.")

def select_sentiment_dates():
    """Allow user to specify a date range for sentiment analysis (optional)."""
    start_date = input("Enter the start date for sentiment analysis (YYYY-MM-DD) or press Enter to skip: ")
    end_date = input("Enter the end date for sentiment analysis (YYYY-MM-DD) or press Enter to skip: ")
    return start_date if start_date else None, end_date if end_date else None

def main():
    portfolios = load_portfolios()
    print("Welcome to the Portfolio Tracker!")
    
    username = input("Enter your username: ")

    # Step 1: Choose to create, add to, or view a portfolio
    action = input("Would you like to 'create' a new portfolio, 'add' to an existing portfolio, or 'view' your portfolio? ").lower()

    if action == 'create' or action == 'add':
        create_or_add_portfolio(portfolios, username, action)
    elif action == 'view':
        view_portfolio(portfolios, username)
    else:
        print("Invalid action. Please enter 'create', 'add', or 'view'.")

if __name__ == "__main__":
    main()
