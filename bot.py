import requests
import pandas as pd
from ta.momentum import RSIIndicator
from ta.trend import MACD
from ta.volatility import BollingerBands
import time
import pytz

LOOKBACK = 1  # Number of days to fetch historical prices

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

# Real-Time Execution
def main():
    print("Starting Real-Time Trading Bot...")
    while True:
        symbol = input("Enter the cryptocurrency symbol (or 'exit' to quit): ").strip().lower()
        if symbol == 'exit':
            print("Exiting the bot.")
            break
        while True:
            try:
                data = fetch_data(symbol, LOOKBACK)
                if data.empty:
                    print("No data fetched, skipping this iteration.")
                    time.sleep(60)
                    continue
                data = calculate_indicators(data)
                data = generate_signals(data)
                print(data.tail(1))  # Print the latest data with signals
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

if __name__ == "__main__":
    main()