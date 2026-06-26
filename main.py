import time
from config import SYMBOLS, CHECK_INTERVAL_MINUTES, RSI_PERIOD, PIP_SIZES
from market import get_candles
from indicators import add_rsi
from strategy import generate_signal
from telegram_bot import send_signal


def run_once():
    for symbol in SYMBOLS:
        df = get_candles(symbol)
        if df is None or df.empty:
            continue

        df = add_rsi(df, period=RSI_PERIOD)
        pip_size = PIP_SIZES.get(symbol, 0.0001)
        signal = generate_signal(df, pip_size=pip_size)

        if signal:
            print(f"[{symbol}] Signal topildi: {signal['direction']}")
            send_signal(symbol, signal)
        else:
            print(f"[{symbol}] Signal yo'q.")


def main():
    print("Forex signal bot ishga tushdi...")
    while True:
        run_once()
        print(f"{CHECK_INTERVAL_MINUTES} daqiqa kutilmoqda...\n")
        time.sleep(CHECK_INTERVAL_MINUTES * 60)


if __name__ == "__main__":
    main()
