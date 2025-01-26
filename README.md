# Real-Time Cryptocurrency Trading Bot of Crypto Pixel

This is a real-time cryptocurrency trading bot that fetches historical data from the Coingecko API, calculates technical indicators, and generates buy/sell signals based on the calculated indicators.

## Features

- Fetches historical data for a specified cryptocurrency from the Coingecko API
- Calculates technical indicators such as RSI, MACD, and Bollinger Bands
- Generates buy/sell signals based on the calculated indicators
- Converts timestamps to Pacific Standard Time (PST)
- Runs in real-time, fetching data and generating signals every 60 seconds

## Requirements

- Python 3.6+
- `requests`
- `pandas`
- `ta`
- `pytz`

## Installation

1. Install the required packages:
    ```sh
    pip install -r requirements.txt
    ```

## Usage

1. Update the [SYMBOL](http://_vscodecontentref_/0) variable in [bot.py](http://_vscodecontentref_/1) to the cryptocurrency you want to trade (e.g., "bitcoin", "solana").
2. Run the bot:
    ```sh
    python bot.py
    ```

## Configuration

You can configure the following parameters in [bot.py](http://_vscodecontentref_/2):

- [SYMBOL](http://_vscodecontentref_/3): The cryptocurrency to trade (default: "solana")
- [LOOKBACK](http://_vscodecontentref_/4): Number of days to fetch historical data (default: 1)
- [RISK_PERCENTAGE](http://_vscodecontentref_/5): Risk per trade as a percentage of account balance (default: 1)
- [TAKE_PROFIT_MULTIPLIER](http://_vscodecontentref_/6): Take-profit relative to stop-loss (default: 2)

## License

This project is licensed under the MIT License. See the LICENSE file for details.

## Disclaimer

This bot is for educational purposes only. Trading cryptocurrencies involves significant risk and can result in substantial losses. Use this bot at your own risk.