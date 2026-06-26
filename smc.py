import pandas as pd


def find_swing_points(df: pd.DataFrame, window: int = 2) -> pd.DataFrame:
    """
    Swing high/low (fraktal) nuqtalarini topadi.
    Bir nuqta swing high bo'ladi, agar u ikki tarafidagi 'window' ta candle'dan
    balandroq bo'lsa. Swing low uchun teskarisi. Bu nuqtalar likvidlik zonalarini
    aniqlash uchun asos bo'ladi (equal highs/lows shu nuqtalardan tashkil topadi).
    """
    highs = df["high"]
    lows = df["low"]

    swing_high = pd.Series(False, index=df.index)
    swing_low = pd.Series(False, index=df.index)

    for i in range(window, len(df) - window):
        local_highs = highs[i - window:i + window + 1]
        local_lows = lows[i - window:i + window + 1]

        if highs[i] == local_highs.max():
            swing_high[i] = True
        if lows[i] == local_lows.min():
            swing_low[i] = True

    df["swing_high"] = swing_high
    df["swing_low"] = swing_low
    return df


def find_liquidity_pools(df: pd.DataFrame, pip_size: float, tolerance_pips: float = 5, lookback: int = 60):
    """
    Likvidlik zonalarini (equal highs / equal lows) topadi.
    Bir-biriga yaqin (tolerance ichida) joylashgan swing high'lar -> yuqori likvidlik
    zonasi (yuqorida sotuvchilar stoplari/likvidligi yotgan joy).
    Bir-biriga yaqin swing low'lar -> past likvidlik zonasi.
    Qancha ko'p nuqta bitta zonaga tushsa, shuncha "kuchli" likvidlik hisoblanadi.
    """
    recent = df.iloc[-lookback:]
    tolerance = tolerance_pips * pip_size

    def cluster(points):
        pools = []
        for p in sorted(points):
            placed = False
            for pool in pools:
                if abs(p - pool["level"]) <= tolerance:
                    pool["levels"].append(p)
                    pool["level"] = sum(pool["levels"]) / len(pool["levels"])
                    pool["touches"] += 1
                    placed = True
                    break
            if not placed:
                pools.append({"level": p, "levels": [p], "touches": 1})
        return pools

    high_points = recent.loc[recent["swing_high"], "high"].tolist()
    low_points = recent.loc[recent["swing_low"], "low"].tolist()

    pools = []
    for pool in cluster(high_points):
        pools.append({"level": pool["level"], "type": "high", "touches": pool["touches"]})
    for pool in cluster(low_points):
        pools.append({"level": pool["level"], "type": "low", "touches": pool["touches"]})

    return pools


def detect_liquidity_sweep(df: pd.DataFrame, pools: list, pip_size: float, wick_margin_pips: float = 2):
    """
    Oxirgi candle biror likvidlik zonasini "supurib" (sweep) o'tib, lekin yopilishda
    qarama-qarshi tomonga qaytganini (rejection) tekshiradi - bu Smart Money'ning
    stop-hunt qilib, narxni teskari yo'nalishga burayotgani belgisi.

    Natija: (direction, supurilgan_zona, sweep_candle) yoki (None, None, None)
    """
    last = df.iloc[-1]
    margin = wick_margin_pips * pip_size

    for pool in pools:
        if pool["type"] == "low":
            # narx pastdagi likvidlikni supurib o'tdi, lekin yopilishda qaytib chiqdi -> bullish
            if last["low"] < pool["level"] - margin and last["close"] > pool["level"]:
                return "BUY", pool, last
        else:
            # narx yuqoridagi likvidlikni supurib o'tdi, lekin yopilishda qaytib tushdi -> bearish
            if last["high"] > pool["level"] + margin and last["close"] < pool["level"]:
                return "SELL", pool, last

    return None, None, None


def find_liquidity_target(pools: list, direction: str, current_price: float):
    """
    Signal yo'nalishi bo'yicha keyingi, hali "supurilmagan" likvidlik zonasini topadi.
    Bu - TP (take profit) nishoni bo'ladi, chunki narx odatda keyingi likvidlik
    yotgan joyga qarab harakatlanadi.

    BUY uchun -> eng yaqin yuqoridagi 'high' zona
    SELL uchun -> eng yaqin pastdagi 'low' zona
    """
    if direction == "BUY":
        candidates = [p for p in pools if p["type"] == "high" and p["level"] > current_price]
        if candidates:
            return min(candidates, key=lambda p: p["level"])
    else:
        candidates = [p for p in pools if p["type"] == "low" and p["level"] < current_price]
        if candidates:
            return max(candidates, key=lambda p: p["level"])

    return None
