import yfinance as yf
from .models import Stock, HistoricalPrice

def get_stock_data(symbol):
    symbol = symbol.strip().upper()

    ticker = yf.Ticker(symbol)

    try:
        info = ticker.info
    except Exception:
        raise ValueError(
            f"Invalid stock symbol: {symbol}"
        )

    if not info or not info.get("symbol"):
        raise ValueError(
            f"Invalid stock symbol: {symbol}"
        )

    price = info.get("currentPrice")

    if price is None or price <= 0:
        raise ValueError(
            f"Invalid stock symbol: {symbol}"
        )

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


def get_historical_data(symbol):
    symbol = symbol.strip().upper()

    try:
        stock = Stock.objects.get(symbol=symbol)
    except Stock.DoesNotExist:
        raise ValueError(
            f"Stock not found: {symbol}"
        )

    ticker = yf.Ticker(symbol)

    try:
        history = ticker.history(period="1y")
    except Exception:
        raise ValueError(
            f"Unable to fetch historical data for: {symbol}"
        )

    if history.empty:
        raise ValueError(
            f"No historical data found for: {symbol}"
        )

    for date, row in history.iterrows():
        HistoricalPrice.objects.update_or_create(
            stock=stock,
            date=date.date(),
            defaults={
                "open": row["Open"],
                "high": row["High"],
                "low": row["Low"],
                "close": row["Close"],
                "volume": row["Volume"],
            },
        )

    return HistoricalPrice.objects.filter(
        stock=stock
    ).order_by("date")


def calculate_sma(symbol, window=20):
    symbol = symbol.strip().upper()

    try:
        stock = Stock.objects.get(symbol=symbol)
    except Stock.DoesNotExist:
        raise ValueError(
            f"Stock not found: {symbol}"
        )

    history = HistoricalPrice.objects.filter(
        stock=stock
    ).order_by("date")

    if history.count() < window:
        raise ValueError(
            f"Not enough historical data for {window}-day SMA"
        )

    prices = [float(item.close) for item in history]

    sma_values = []

    for i in range(window - 1, len(prices)):
        window_prices = prices[
            i - window + 1:i + 1
        ]

        sma = sum(window_prices) / window

        sma_values.append({
            "date": history[i].date,
            "close": prices[i],
            "sma": round(sma, 2)
        })

    return {
        "symbol": symbol,
        "indicator": f"SMA_{window}",
        "data": sma_values
    }
def calculate_ema(symbol, window=20):
    symbol = symbol.strip().upper()

    try:
        stock = Stock.objects.get(symbol=symbol)
    except Stock.DoesNotExist:
        raise ValueError(
            f"Stock not found: {symbol}"
        )

    history = HistoricalPrice.objects.filter(
        stock=stock
    ).order_by("date")

    if history.count() < window:
        raise ValueError(
            f"Not enough historical data for {window}-day EMA"
        )

    prices = [float(item.close) for item in history]

    multiplier = 2 / (window + 1)

    ema_values = []

    first_ema = sum(prices[:window]) / window

    ema_values.append({
        "date": history[window - 1].date,
        "close": prices[window - 1],
        "ema": round(first_ema, 2)
    })

    previous_ema = first_ema

    for i in range(window, len(prices)):
        current_price = prices[i]

        current_ema = (
            (current_price * multiplier)
            + (previous_ema * (1 - multiplier))
        )

        ema_values.append({
            "date": history[i].date,
            "close": current_price,
            "ema": round(current_ema, 2)
        })

        previous_ema = current_ema

    return {
        "symbol": symbol,
        "indicator": f"EMA_{window}",
        "data": ema_values
    }
