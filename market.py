import requests
import pandas as pd
from config import TWELVE_DATA_API_KEY, INTERVAL, CANDLES_COUNT

BASE_URL = "https://api.twelvedata.com/time_series"


def get_candles(symbol: str):
    """
    Twelve Data API orqali berilgan juftlik uchun OHLC candle ma'lumotlarini oladi.
    Natija: vaqt bo'yicha eskidan-yangiga tartiblangan pandas DataFrame, yoki None (xato bo'lsa).
    """
    params = {
        "symbol": symbol,
        "interval": INTERVAL,
        "outputsize": CANDLES_COUNT,
        "apikey": TWELVE_DATA_API_KEY,
    }

    try:
        response = requests.get(BASE_URL, params=params, timeout=10)
        data = response.json()
    except requests.RequestException as e:
        print(f"[market.py] So'rov xatosi ({symbol}): {e}")
        return None

    if "values" not in data:
        print(f"[market.py] {symbol} uchun ma'lumot topilmadi: {data.get('message', data)}")
        return None

    df = pd.DataFrame(data["values"])
    df = df.rename(columns={"datetime": "time"})

    for col in ["open", "high", "low", "close"]:
        df[col] = df[col].astype(float)

    df = df.iloc[::-1].reset_index(drop=True)  # eskidan yangiga qarab tartiblash
    return df
