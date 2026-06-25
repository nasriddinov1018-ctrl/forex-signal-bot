import requests
import pandas as pd
from config import API_KEY

BASE_URL = "https://api.twelvedata.com/time_series"

def get_data(symbol="EUR/USD", interval="15min"):

    params = {
        "symbol": symbol,
        "interval": interval,
        "outputsize": 200,
        "apikey": API_KEY,
    }

    r = requests.get(BASE_URL, params=params)
    data = r.json()

    if "values" not in data:
        return None

    df = pd.DataFrame(data["values"])

    df = df.iloc[::-1]

    for col in ["open", "high", "low", "close"]:
        df[col] = df[col].astype(float)

    return df
