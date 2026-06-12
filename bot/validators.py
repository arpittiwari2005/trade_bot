"""
Input validators for the trading bot.

Each validator normalizes and validates a single input field,
raising ValueError with a descriptive message on failure.
"""

import re

VALID_SIDES = ("BUY", "SELL")
VALID_ORDER_TYPES = ("MARKET", "LIMIT", "STOP_LIMIT")

# Basic pattern: 2-20 uppercase letters (e.g., BTCUSDT, ETHUSDT)
SYMBOL_PATTERN = re.compile(r"^[A-Z]{2,20}$")


def validate_symbol(symbol: str) -> str:
    """
    Validate and normalize a trading pair symbol.

    Args:
        symbol: Raw symbol input (e.g., "btcusdt").

    Returns:
        Uppercased symbol string.

    Raises:
        ValueError: If symbol is empty or has invalid format.
    """
    if not symbol or not symbol.strip():
        raise ValueError("Symbol is required (e.g., BTCUSDT).")

    symbol = symbol.strip().upper()

    if not SYMBOL_PATTERN.match(symbol):
        raise ValueError(
            f"Invalid symbol '{symbol}'. "
            "Expected 2-20 uppercase letters (e.g., BTCUSDT)."
        )

    return symbol


def validate_side(side: str) -> str:
    """
    Validate order side.

    Args:
        side: Raw side input.

    Returns:
        Uppercased side string ("BUY" or "SELL").

    Raises:
        ValueError: If side is not BUY or SELL.
    """
    if not side or not side.strip():
        raise ValueError("Side is required (BUY or SELL).")

    side = side.strip().upper()

    if side not in VALID_SIDES:
        raise ValueError(
            f"Invalid side '{side}'. Must be one of: {', '.join(VALID_SIDES)}."
        )

    return side


def validate_order_type(order_type: str) -> str:
    """
    Validate order type.

    Args:
        order_type: Raw order type input.

    Returns:
        Uppercased order type string.

    Raises:
        ValueError: If order type is not MARKET, LIMIT, or STOP_LIMIT.
    """
    if not order_type or not order_type.strip():
        raise ValueError("Order type is required (MARKET, LIMIT, or STOP_LIMIT).")

    order_type = order_type.strip().upper()

    if order_type not in VALID_ORDER_TYPES:
        raise ValueError(
            f"Invalid order type '{order_type}'. "
            f"Must be one of: {', '.join(VALID_ORDER_TYPES)}."
        )

    return order_type


def validate_quantity(quantity: str | float) -> float:
    """
    Validate order quantity.

    Args:
        quantity: Raw quantity input (string or float).

    Returns:
        Validated quantity as float.

    Raises:
        ValueError: If quantity is not a positive number.
    """
    try:
        qty = float(quantity)
    except (TypeError, ValueError):
        raise ValueError(
            f"Invalid quantity '{quantity}'. Must be a positive number."
        )

    if qty <= 0:
        raise ValueError(
            f"Invalid quantity '{qty}'. Must be greater than zero."
        )

    return qty


def validate_price(price: str | float | None, required: bool = False) -> float | None:
    """
    Validate order price.

    Args:
        price: Raw price input (string, float, or None).
        required: If True, price cannot be None.

    Returns:
        Validated price as float, or None if not required and not provided.

    Raises:
        ValueError: If price is required but missing, or not a positive number.
    """
    if price is None:
        if required:
            raise ValueError("Price is required for this order type.")
        return None

    try:
        p = float(price)
    except (TypeError, ValueError):
        raise ValueError(f"Invalid price '{price}'. Must be a positive number.")

    if p <= 0:
        raise ValueError(f"Invalid price '{p}'. Must be greater than zero.")

    return p


def validate_stop_price(
    stop_price: str | float | None, required: bool = False
) -> float | None:
    """
    Validate stop price for stop-limit orders.

    Args:
        stop_price: Raw stop price input.
        required: If True, stop_price cannot be None.

    Returns:
        Validated stop price as float, or None.

    Raises:
        ValueError: If stop_price is required but missing, or not a positive number.
    """
    if stop_price is None:
        if required:
            raise ValueError("Stop price is required for STOP_LIMIT orders.")
        return None

    try:
        sp = float(stop_price)
    except (TypeError, ValueError):
        raise ValueError(
            f"Invalid stop price '{stop_price}'. Must be a positive number."
        )

    if sp <= 0:
        raise ValueError(
            f"Invalid stop price '{sp}'. Must be greater than zero."
        )

    return sp
