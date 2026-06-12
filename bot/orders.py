"""
Order placement logic for the trading bot.

Provides high-level functions for placing Market, Limit, and Stop-Limit
orders, each with proper parameter assembly and result extraction.
"""

import logging

from bot.client import BinanceTestnetClient

logger = logging.getLogger("trading_bot.orders")


def _format_order_response(response: dict) -> dict:
    """
    Extract and format key fields from an order API response.

    Args:
        response: Raw order response from the Binance API.

    Returns:
        Dict with the most relevant order fields.
    """
    return {
        "orderId": response.get("orderId"),
        "symbol": response.get("symbol"),
        "side": response.get("side"),
        "type": response.get("type"),
        "status": response.get("status"),
        "quantity": response.get("origQty"),
        "executedQty": response.get("executedQty"),
        "price": response.get("price"),
        "avgPrice": response.get("avgPrice", "N/A"),
        "stopPrice": response.get("stopPrice", "N/A"),
        "timeInForce": response.get("timeInForce", "N/A"),
        "updateTime": response.get("updateTime"),
    }


def place_market_order(
    client: BinanceTestnetClient,
    symbol: str,
    side: str,
    quantity: float,
) -> dict:
    """
    Place a MARKET order.

    Args:
        client: Initialized Binance testnet client.
        symbol: Trading pair (e.g., "BTCUSDT").
        side: "BUY" or "SELL".
        quantity: Order quantity.

    Returns:
        Formatted order response dict.
    """
    logger.info(
        "Placing MARKET order — symbol=%s, side=%s, quantity=%s",
        symbol,
        side,
        quantity,
    )

    response = client.create_order(
        symbol=symbol,
        side=side,
        type="MARKET",
        quantity=quantity,
    )

    result = _format_order_response(response)
    logger.info("MARKET order placed — orderId=%s, status=%s", result["orderId"], result["status"])
    return result


def place_limit_order(
    client: BinanceTestnetClient,
    symbol: str,
    side: str,
    quantity: float,
    price: float,
) -> dict:
    """
    Place a LIMIT order.

    Args:
        client: Initialized Binance testnet client.
        symbol: Trading pair (e.g., "BTCUSDT").
        side: "BUY" or "SELL".
        quantity: Order quantity.
        price: Limit price.

    Returns:
        Formatted order response dict.
    """
    logger.info(
        "Placing LIMIT order — symbol=%s, side=%s, quantity=%s, price=%s",
        symbol,
        side,
        quantity,
        price,
    )

    response = client.create_order(
        symbol=symbol,
        side=side,
        type="LIMIT",
        quantity=quantity,
        price=price,
        timeInForce="GTC",
    )

    result = _format_order_response(response)
    logger.info("LIMIT order placed — orderId=%s, status=%s", result["orderId"], result["status"])
    return result


def place_stop_limit_order(
    client: BinanceTestnetClient,
    symbol: str,
    side: str,
    quantity: float,
    price: float,
    stop_price: float,
) -> dict:
    """
    Place a STOP-LIMIT order (bonus order type).

    The order becomes a LIMIT order once the stop_price is triggered.

    Args:
        client: Initialized Binance testnet client.
        symbol: Trading pair (e.g., "BTCUSDT").
        side: "BUY" or "SELL".
        quantity: Order quantity.
        price: Limit price (after stop is triggered).
        stop_price: Trigger price.

    Returns:
        Formatted order response dict.
    """
    logger.info(
        "Placing STOP_LIMIT order — symbol=%s, side=%s, quantity=%s, "
        "price=%s, stopPrice=%s",
        symbol,
        side,
        quantity,
        price,
        stop_price,
    )

    response = client.create_order(
        symbol=symbol,
        side=side,
        type="STOP",
        quantity=quantity,
        price=price,
        stopPrice=stop_price,
        timeInForce="GTC",
    )

    result = _format_order_response(response)
    logger.info(
        "STOP_LIMIT order placed — orderId=%s, status=%s",
        result["orderId"],
        result["status"],
    )
    return result
