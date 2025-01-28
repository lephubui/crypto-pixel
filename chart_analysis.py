from ta.momentum import RSIIndicator
from ta.trend import MACD
from ta.volatility import BollingerBands

def calculate_indicators(data):
    data['RSI'] = RSIIndicator(data['Close'], window=14).rsi()
    macd = MACD(data['Close'])
    data['MACD'] = macd.macd()
    data['Signal_Line'] = macd.macd_signal()
    bb = BollingerBands(data['Close'])
    data['BB_Upper'] = bb.bollinger_hband()
    data['BB_Lower'] = bb.bollinger_lband()
    return data

def generate_signals(data):
    data['Signal'] = 0
    data.loc[
        (data['RSI'] > 30) & (data['RSI'] < 70), 'Signal'] = 1  # Buy signal
    data.loc[
        (data['RSI'] < 30) | (data['RSI'] > 70), 'Signal'] = -1  # Sell signal
    return data