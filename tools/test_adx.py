from app.storage import load_trades
from app.candles import build_candles
from app.indicators.adx import adx

trades = load_trades()
candles = build_candles(trades, timeframe="1h")

values = adx(candles)

print(len(values))
print(values[-5:])