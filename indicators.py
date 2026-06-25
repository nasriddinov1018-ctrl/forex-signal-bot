import pandas as pd

def ema(data, period):
    return data["close"].ewm(span=period, adjust=False).mean()

def rsi(data, period=14):
    delta = data["close"].diff()

    gain = delta.where(delta > 0, 0)
    loss = -delta.where(delta < 0, 0)

    avg_gain = gain.rolling(period).mean()
    avg_loss = loss.rolling(period).mean()

    rs = avg_gain / avg_loss

    return 100 - (100 / (1 + rs))
