from ta.momentum import RSIIndicator
from ta.trend import MACD, SMAIndicator, EMAIndicator
from ta.volatility import BollingerBands

def calculate_indicators(data):
    data['RSI'] = RSIIndicator(data['Close'], window=14).rsi()
    macd = MACD(data['Close'])
    data['MACD'] = macd.macd()
    data['Signal_Line'] = macd.macd_signal()
    bb = BollingerBands(data['Close'])
    data['BB_Upper'] = bb.bollinger_hband()
    data['BB_Lower'] = bb.bollinger_lband()
    data['SMA_50'] = SMAIndicator(data['Close'], window=50).sma_indicator()
    data['SMA_200'] = SMAIndicator(data['Close'], window=200).sma_indicator()
    data['EMA_50'] = EMAIndicator(data['Close'], window=50).ema_indicator()
    data['EMA_200'] = EMAIndicator(data['Close'], window=200).ema_indicator()
    return data

def generate_signals(data):
    data['Signal'] = 0
    data.loc[
        (data['RSI'] > 30) & (data['RSI'] < 70), 'Signal'] = 1  # Buy signal
    data.loc[
        (data['RSI'] < 30) | (data['RSI'] > 70), 'Signal'] = -1  # Sell signal
    return data