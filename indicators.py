import pandas as pd


def add_rsi(df: pd.DataFrame, period: int = 14) -> pd.DataFrame:
    delta = df["close"].diff()
    gain = delta.where(delta > 0, 0.0)
    loss = -delta.where(delta < 0, 0.0)

    avg_gain = gain.rolling(window=period).mean()
    avg_loss = loss.rolling(window=period).mean()

    rs = avg_gain / avg_loss
    df["rsi"] = 100 - (100 / (1 + rs))
    return df


def add_ema(df: pd.DataFrame, period: int, column_name: str) -> pd.DataFrame:
    df[column_name] = df["close"].ewm(span=period, adjust=False).mean()
    return df


def add_macd(df: pd.DataFrame, fast: int = 12, slow: int = 26, signal: int = 9) -> pd.DataFrame:
    ema_fast = df["close"].ewm(span=fast, adjust=False).mean()
    ema_slow = df["close"].ewm(span=slow, adjust=False).mean()
    df["macd"] = ema_fast - ema_slow
    df["macd_signal"] = df["macd"].ewm(span=signal, adjust=False).mean()
    df["macd_hist"] = df["macd"] - df["macd_signal"]
    return df


def calculate_all(df: pd.DataFrame, rsi_period=14, ema_fast=9, ema_slow=21) -> pd.DataFrame:
    df = add_rsi(df, rsi_period)
    df = add_ema(df, ema_fast, "ema_fast")
    df = add_ema(df, ema_slow, "ema_slow")
    df = add_macd(df)
    return df
