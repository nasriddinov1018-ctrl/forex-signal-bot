from config import MIN_RISK_REWARD, SL_BUFFER_PIPS, LIQUIDITY_TOLERANCE_PIPS, SWEEP_WICK_MARGIN_PIPS
from smc import find_swing_points, find_liquidity_pools, detect_liquidity_sweep, find_liquidity_target


def generate_signal(df, pip_size: float = 0.0001):
    """
    Likvidlik (liquidity) asosidagi SMC strategiyasi:
      1. Swing nuqtalardan likvidlik zonalari (equal highs/lows) topiladi
      2. Oxirgi candle shu zonalardan birini "supurib" (sweep) qaytganini tekshiradi
      3. SL - supurilgan zonadan tashqariga (institutsional stoplar allaqachon
         ishga tushgan joy, demak qaytib supurilishi ehtimoli past)
      4. TP - hali supurilmagan keyingi likvidlik zonasi (topilmasa, RR nisbati
         asosida hisoblanadi)
    """
    if len(df) < 30:
        return None

    df = find_swing_points(df)
    pools = find_liquidity_pools(df, pip_size=pip_size, tolerance_pips=LIQUIDITY_TOLERANCE_PIPS)

    direction, swept_pool, sweep_candle = detect_liquidity_sweep(
        df, pools, pip_size=pip_size, wick_margin_pips=SWEEP_WICK_MARGIN_PIPS
    )

    if direction is None:
        return None

    last_close = df["close"].iloc[-1]
    last_rsi = df["rsi"].iloc[-1] if "rsi" in df.columns else None

    # RSI bilan qo'shimcha filtr - haddan tashqari kuchsiz signallarni o'tkazib yuborish
    if direction == "BUY" and last_rsi is not None and last_rsi > 75:
        return None
    if direction == "SELL" and last_rsi is not None and last_rsi < 25:
        return None

    # --- SL: supurilgan likvidlik zonasidan tashqariga ---
    if direction == "BUY":
        sl = sweep_candle["low"] - SL_BUFFER_PIPS * pip_size
        risk = last_close - sl
    else:
        sl = sweep_candle["high"] + SL_BUFFER_PIPS * pip_size
        risk = sl - last_close

    if risk is None or risk <= 0:
        return None

    # --- TP: keyingi supurilmagan likvidlik zonasi, bo'lmasa RR nisbati ---
    target_pool = find_liquidity_target(pools, direction, last_close)
    if target_pool:
        tp = target_pool["level"]
        tp_source = f"Likvidlik zonasi ({target_pool['touches']} ta urinish)"
        reward = abs(tp - last_close)
        if reward < risk * 1.2:  # zona juda yaqin, foyda kam bo'ladi
            tp = last_close + risk * MIN_RISK_REWARD if direction == "BUY" else last_close - risk * MIN_RISK_REWARD
            tp_source = f"RR nisbati (1:{MIN_RISK_REWARD})"
    else:
        tp = last_close + risk * MIN_RISK_REWARD if direction == "BUY" else last_close - risk * MIN_RISK_REWARD
        tp_source = f"RR nisbati (1:{MIN_RISK_REWARD})"

    risk_reward = round(abs(tp - last_close) / risk, 2)

    reasons = [
        f"Likvidlik supurildi: {swept_pool['type']} zona @ {round(swept_pool['level'], 5)} ({swept_pool['touches']} ta urinish)",
        f"TP manbasi: {tp_source}",
    ]
    if last_rsi is not None:
        reasons.append(f"RSI={last_rsi:.1f}")

    return {
        "direction": direction,
        "entry": round(last_close, 5),
        "sl": round(sl, 5),
        "tp": round(tp, 5),
        "risk_reward": risk_reward,
        "reasons": reasons,
      }
