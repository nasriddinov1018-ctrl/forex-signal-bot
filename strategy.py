from indicators import ema, rsi

def check_signal(df):
    df["EMA50"] = ema(df, 50)
    df["EMA200"] = ema(df, 200)
    df["RSI"] = rsi(df)

    last = df.iloc[-1]

    if last["EMA50"] > last["EMA200"] and last["RSI"] > 55:
        return "BUY"

    if last["EMA50"] < last["EMA200"] and last["RSI"] < 45:
        return "SELL"

    return None
