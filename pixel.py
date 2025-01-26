import requests
import time

def get_bitcoin_price():
    url = "https://api.coingecko.com/api/v3/simple/price"
    params = {
        "ids": "bitcoin",
        "vs_currencies": "usd"
    }
    response = requests.get(url, params=params)
    data = response.json()
    return data["bitcoin"]["usd"]

def get_bitcoin_data():
    url = "https://api.coingecko.com/api/v3/coins/bitcoin"
    response = requests.get(url)
    data = response.json()
    return data

if __name__ == "__main__":
    while True:
        price = get_bitcoin_price()
        print(f"Current Bitcoin price: ${price}")
        time.sleep(60)  # Fetch the price every 60 seconds