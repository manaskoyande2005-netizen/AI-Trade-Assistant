import yfinance as yf
from .models import Stock

def get_stock_data(symbol):
    symbol = symbol.strip().upper()
    ticker = yf.Ticker(symbol)

    try:
        info = ticker.info
    except Exception:
        raise ValueError(f"Invalid stock symbol: {symbol}")

    if not info or not info.get("symbol"):
        raise ValueError(f"Invalid stock symbol: {symbol}")

    price = info.get("currentPrice")

    if price is None or price <= 0:
        raise ValueError(f"Invalid stock symbol: {symbol}")

    stock_data = {
        "symbol": symbol,
        "company_name": info.get("longName", ""),
        "price": price,
        "currency": info.get("currency"),
        "volume": info.get("volume", 0),
        "market_cap": info.get("marketCap"),
    }

    stock, created = Stock.objects.update_or_create(
        symbol=stock_data["symbol"],
        defaults={
            "company_name": stock_data["company_name"],
            "price": stock_data["price"],
            "currency": stock_data["currency"],
            "volume": stock_data["volume"],
            "market_cap": stock_data["market_cap"],
        },
    )

    return stock

