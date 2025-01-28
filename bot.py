import requests
import pandas as pd
from ta.momentum import RSIIndicator
from ta.trend import MACD
from ta.volatility import BollingerBands
import time
import pytz
import configparser
import openai
from telegram_bot import send_telegram_message  # Import the send_telegram_message function

# Read configuration file
config = configparser.ConfigParser()
config.read('config.ini')

LOOKBACK = 1  # Number of days to fetch historical prices
OPENAI_API_KEY = config['openai']['api_key']
NEWS_API_KEY = config['newsapi']['api_key']

# Initialize OpenAI API
openai.api_key = OPENAI_API_KEY

# Fetch list of top 5 coins by market cap
def fetch_top_coins():
    url = "https://api.coingecko.com/api/v3/coins/markets"
    params = {
        "vs_currency": "usd",
        "order": "market_cap_desc",
        "per_page": 5,
        "page": 1
    }
    response = requests.get(url, params=params)
    data = response.json()
    return data

# Fetch Historical Data
def fetch_data(symbol, lookback):
    url = f"https://api.coingecko.com/api/v3/coins/{symbol}/market_chart"
    params = {
        "vs_currency": "usd",
        "days": lookback
    }
    response = requests.get(url, params=params)
    data = response.json()
    
    if 'prices' not in data:
        print("Error: 'prices' key not found in the response")
        print("Response:", data)
        return pd.DataFrame()  # Return an empty DataFrame
    
    ohlcv = data["prices"]
    df = pd.DataFrame(ohlcv, columns=["Timestamp", "Close"])
    df["Timestamp"] = pd.to_datetime(df["Timestamp"], unit="ms")
    
    # Convert Timestamp to Pacific Time
    pacific = pytz.timezone('US/Pacific')
    df["Timestamp"] = df["Timestamp"].dt.tz_localize('UTC').dt.tz_convert(pacific)
    
    df["Open"] = df["Close"].shift(1)
    df["High"] = df["Close"].rolling(window=2).max()
    df["Low"] = df["Close"].rolling(window=2).min()
    df["Volume"] = 0  # Coingecko API does not provide volume data
    df = df.dropna()
    return df

# Calculate Indicators
def calculate_indicators(data):
    data['RSI'] = RSIIndicator(data['Close'], window=14).rsi()
    macd = MACD(data['Close'])
    data['MACD'] = macd.macd()
    data['Signal_Line'] = macd.macd_signal()
    bb = BollingerBands(data['Close'])
    data['BB_Upper'] = bb.bollinger_hband()
    data['BB_Lower'] = bb.bollinger_lband()
    return data

# Generate Buy/Sell Signals
def generate_signals(data):
    data['Signal'] = 0
    data.loc[
        (data['RSI'] > 30) & (data['RSI'] < 70), 'Signal'] = 1  # Buy signal
    data.loc[
        (data['RSI'] < 30) | (data['RSI'] > 70), 'Signal'] = -1  # Sell signal
    return data

# Fetch current news related to the cryptocurrency
def fetch_news(symbol):
    url = f"https://newsapi.org/v2/everything?q={symbol}&apiKey={NEWS_API_KEY}"
    response = requests.get(url)
    data = response.json()
    articles = data.get('articles', [])
    return articles

# Analyze signal and news using ChatGPT
def analyze_with_chatgpt(symbol, latest_data, news_articles):
    prompt = f"Analyze the following data for {symbol}:\n\n{latest_data.to_string(index=False)}\n\n"
    prompt += "Here are the latest news articles:\n"
    for article in news_articles:
        prompt += f"- {article['title']}: {article['description']}\n"
    
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a financial analyst."},
            {"role": "user", "content": prompt}
        ],
        max_tokens=500
    )
    analysis = response['choices'][0]['message']['content'].strip()
    return analysis

# Process data and send signals
def process_data(symbol):
    while True:
        try:
            data = fetch_data(symbol, LOOKBACK)
            if data.empty:
                print("No data fetched, skipping this iteration.")
                time.sleep(60)
                continue
            data = calculate_indicators(data)
            data = generate_signals(data)
            latest_data = data.tail(1)
            print(latest_data)  # Print the latest data with signals
            
            news_articles = fetch_news(symbol)
            analysis = analyze_with_chatgpt(symbol, latest_data, news_articles)
            
            # send_telegram_message(symbol, latest_data, analysis)
            print(analysis)
        except Exception as e:
            print(f"Error: {e}")
            print("Exception details:", e.__class__.__name__, e)
        time.sleep(60)  # Fetch data every 60 seconds
        user_input = input("Enter 'switch' to change symbol or 'continue' to keep running: ").strip().lower()
        if user_input == 'switch':
            break
        elif user_input == 'exit':
            print("Exiting the bot.")
            return

# Main function
def main():
    print("Starting Real-Time Trading Bot...")
    while True:
        coin_list = fetch_top_coins()
        print("Top 5 coins by market cap:")
        for coin in coin_list:
            print(f"{coin['id']}: {coin['name']} ({coin['symbol']})")
        
        user_input = input("Enter the cryptocurrency symbol or name (or 'exit' to quit): ").strip().lower()
        if user_input == 'exit':
            print("Exiting the bot.")
            break
        
        # Find the coin by symbol or name
        symbol = None
        for coin in coin_list:
            if user_input == coin['symbol'].lower() or user_input == coin['name'].lower():
                symbol = coin['id']
                break
        
        if not symbol:
            print("Invalid symbol or name. Please try again.")
            continue
        
        process_data(symbol)

if __name__ == "__main__":
    main()