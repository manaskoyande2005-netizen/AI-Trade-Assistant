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

def calculate_rsi(symbol, window=14):
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

    if history.count() <= window:
        raise ValueError(
            f"Not enough historical data for {window}-day RSI"
        )

    prices = [float(item.close) for item in history]

    gains = []
    losses = []

    for i in range(1, len(prices)):
        change = prices[i] - prices[i - 1]

        if change > 0:
            gains.append(change)
            losses.append(0)

        else:
            gains.append(0)
            losses.append(abs(change))

    rsi_values = []

    average_gain = sum(gains[:window]) / window
    average_loss = sum(losses[:window]) / window

    if average_loss == 0:
        rsi = 100
    else:
        rs = average_gain / average_loss
        rsi = 100 - (100 / (1 + rs))

    rsi_values.append({
        "date": history[window].date(),
        "close": prices[window],
        "rsi": round(rsi, 2)
    })

    for i in range(window, len(gains)):
        average_gain = (
            (average_gain * (window - 1)) + gains[i]
        ) / window

        average_loss = (
            (average_loss * (window - 1)) + losses[i]
        ) / window

        if average_loss == 0:
            rsi = 100
        else:
            rs = average_gain / average_loss
            rsi = 100 - (100 / (1 + rs))

        rsi_values.append({
            "date": history[i + 1].date(),
            "close": prices[i + 1],
            "rsi": round(rsi, 2)
        })

    return {
        "symbol": symbol,
        "indicator": f"RSI_{window}",
        "data": rsi_values
    }

def calculate_macd(symbol):
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

    if history.count() < 26:
        raise ValueError(
            "Not enough historical data for MACD"
        )

    prices = [float(item.close) for item in history]

 
    multiplier_12 = 2 / (12 + 1)

    ema_12 = []
    first_ema_12 = sum(prices[:12]) / 12
    ema_12.append(first_ema_12)

    previous_ema = first_ema_12

    for price in prices[12:]:
        current_ema = (
            (price * multiplier_12)
            + (previous_ema * (1 - multiplier_12))
        )

        ema_12.append(current_ema)
        previous_ema = current_ema

    multiplier_26 = 2 / (26 + 1)

    ema_26 = []
    first_ema_26 = sum(prices[:26]) / 26
    ema_26.append(first_ema_26)

    previous_ema = first_ema_26

    for price in prices[26:]:
        current_ema = (
            (price * multiplier_26)
            + (previous_ema * (1 - multiplier_26))
        )

        ema_26.append(current_ema)
        previous_ema = current_ema

    ema_12_aligned = ema_12[14:]

    macd_values = []

    for i in range(len(ema_26)):
        macd = ema_12_aligned[i] - ema_26[i]

        macd_values.append({
            "date": history[i + 25].date,
            "macd": round(macd, 2)
        })

   
    if len(macd_values) < 9:
        raise ValueError(
            "Not enough data for MACD signal line"
        )

    macd_prices = [
        item["macd"] for item in macd_values
    ]

    multiplier_signal = 2 / (9 + 1)

    first_signal = sum(macd_prices[:9]) / 9

    macd_values[8]["signal"] = round(first_signal, 2)
    macd_values[8]["histogram"] = round(
        macd_prices[8] - first_signal,
        2
    )

    previous_signal = first_signal

    for i in range(9, len(macd_prices)):
        current_signal = (
            (macd_prices[i] * multiplier_signal)
            + (previous_signal * (1 - multiplier_signal))
        )

        macd_values[i]["signal"] = round(
            current_signal,
            2
        )

        macd_values[i]["histogram"] = round(
            macd_prices[i] - current_signal,
            2
        )

        previous_signal = current_signal

    macd_values = macd_values[8:]

    return {
        "symbol": symbol,
        "indicator": "MACD",
        "data": macd_values
    }