from flask import Flask, render_template, jsonify
import pandas as pd
import configparser
from chart_analysis import calculate_indicators, generate_signals
from openai_integration import analyze_with_chatgpt
from telegram_bot import send_telegram_message
import requests
import pytz

app = Flask(__name__)

# Read configuration file
config = configparser.ConfigParser()
config.read('config.ini')

LOOKBACK = 1  # Number of days to fetch historical prices
NEWS_API_KEY = config['newsapi']['api_key']

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

# Fetch current news related to the cryptocurrency
def fetch_news(symbol):
    url = f"https://newsapi.org/v2/everything?q={symbol}&apiKey={NEWS_API_KEY}"
    response = requests.get(url)
    data = response.json()
    articles = data.get('articles', [])
    return articles

@app.route('/')
def index():
    coin_list = fetch_top_coins()
    return render_template('index.html', coins=coin_list)

@app.route('/data/<symbol>')
def data(symbol):
    data = fetch_data(symbol, LOOKBACK)
    data = calculate_indicators(data)
    data = generate_signals(data)
    latest_data = data.tail(1)
    news_articles = fetch_news(symbol)
    analysis = analyze_with_chatgpt(symbol, latest_data, news_articles)
    return jsonify({
        'data': data.to_dict(orient='records'),
        'news': news_articles,
        'analysis': analysis
    })

if __name__ == '__main__':
    app.run(debug=True)