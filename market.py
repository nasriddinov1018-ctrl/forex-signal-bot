import requests

API_KEY = "d6516ae7d2fe48969352b441 f7ba6e3d"

def get_price(symbol="EUR/USD", interval="15min"):
    url = (
        f"https://api.twelvedata.com/time_series?"
        f"symbol={symbol}&interval={interval}&outputsize=200&apikey={API_KEY}"
    )

    response = requests.get(url)
    return response.json()
