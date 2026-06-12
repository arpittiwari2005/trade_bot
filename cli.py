#!/usr/bin/env python3
"""
CLI entry point for the Binance Futures Testnet Trading Bot.

Usage:
    python cli.py order --symbol BTCUSDT --side BUY --type MARKET --quantity 0.001
    python cli.py order --symbol BTCUSDT --side BUY --type LIMIT --quantity 0.001 --price 50000
    python cli.py order --symbol ETHUSDT --side SELL --type STOP_LIMIT --quantity 0.01 --price 3000 --stop-price 3100
"""

import os
import sys

import click
from dotenv import load_dotenv

from bot.client import BinanceAPIError, BinanceTestnetClient
from bot.logging_config import setup_logging
from bot.orders import place_limit_order, place_market_order, place_stop_limit_order
from bot.validators import (
    validate_order_type,
    validate_price,
    validate_quantity,
    validate_side,
    validate_stop_price,
    validate_symbol,
)

# Load environment variables from .env file
load_dotenv()


# ── Helpers ──────────────────────────────────────────────────────────


def _print_header(text: str):
    """Print a styled section header."""
    click.echo()
    click.secho(f"{'─' * 50}", fg="cyan")
    click.secho(f"  {text}", fg="cyan", bold=True)
    click.secho(f"{'─' * 50}", fg="cyan")


def _print_kv(key: str, value, key_color: str = "white"):
    """Print a key-value pair with alignment."""
    click.echo(f"  {click.style(f'{key + ':':<16}', fg=key_color)} {value}")


def _print_order_summary(symbol, side, order_type, quantity, price, stop_price):
    """Print a formatted order request summary before placement."""
    _print_header("📋 Order Request Summary")
    _print_kv("Symbol", symbol)
    _print_kv("Side", click.style(side, fg="green" if side == "BUY" else "red", bold=True))
    _print_kv("Type", order_type)
    _print_kv("Quantity", quantity)
    if price is not None:
        _print_kv("Price", price)
    if stop_price is not None:
        _print_kv("Stop Price", stop_price)
    click.echo()


def _print_order_result(result: dict):
    """Print a formatted order response."""
    status = result.get("status", "UNKNOWN")
    is_filled = status == "FILLED"

    _print_header("✅ Order Response" if is_filled else "📨 Order Placed")
    _print_kv("Order ID", result["orderId"], key_color="yellow")
    _print_kv("Symbol", result["symbol"])
    _print_kv(
        "Side",
        click.style(
            result["side"],
            fg="green" if result["side"] == "BUY" else "red",
            bold=True,
        ),
    )
    _print_kv("Type", result["type"])
    _print_kv(
        "Status",
        click.style(status, fg="green" if is_filled else "yellow", bold=True),
    )
    _print_kv("Quantity", result["quantity"])
    _print_kv("Executed Qty", result["executedQty"])
    _print_kv("Price", result["price"])

    if result.get("avgPrice") and result["avgPrice"] != "N/A":
        _print_kv("Avg Price", result["avgPrice"])
    if result.get("stopPrice") and result["stopPrice"] != "N/A":
        _print_kv("Stop Price", result["stopPrice"])
    if result.get("timeInForce") and result["timeInForce"] != "N/A":
        _print_kv("Time In Force", result["timeInForce"])

    click.echo()
    if is_filled:
        click.secho("  ✅ Order filled successfully!", fg="green", bold=True)
    else:
        click.secho(f"  📨 Order accepted (status: {status})", fg="yellow", bold=True)
    click.echo()


# ── CLI Commands ─────────────────────────────────────────────────────


@click.group()
@click.option(
    "--verbose", "-v", is_flag=True, default=False, help="Enable verbose (DEBUG) console output."
)
@click.pass_context
def cli(ctx, verbose):
    """
    🤖 Binance Futures Testnet Trading Bot

    Place Market, Limit, and Stop-Limit orders on Binance Futures
    Testnet (USDT-M) with structured logging and validation.
    """
    ctx.ensure_object(dict)
    import logging as _logging

    log_level = _logging.DEBUG if verbose else _logging.INFO
    logger = setup_logging(console_level=log_level)
    ctx.obj["logger"] = logger


@cli.command()
@click.option("--symbol", "-s", required=True, help="Trading pair (e.g., BTCUSDT).")
@click.option("--side", required=True, type=click.Choice(["BUY", "SELL"], case_sensitive=False), help="Order side.")
@click.option(
    "--type",
    "order_type",
    required=True,
    type=click.Choice(["MARKET", "LIMIT", "STOP_LIMIT"], case_sensitive=False),
    help="Order type.",
)
@click.option("--quantity", "-q", required=True, type=float, help="Order quantity.")
@click.option("--price", "-p", type=float, default=None, help="Limit price (required for LIMIT / STOP_LIMIT).")
@click.option("--stop-price", type=float, default=None, help="Stop trigger price (required for STOP_LIMIT).")
@click.option("--yes", "-y", is_flag=True, default=False, help="Skip confirmation prompt.")
@click.pass_context
def order(ctx, symbol, side, order_type, quantity, price, stop_price, yes):
    """
    Place an order on Binance Futures Testnet.

    \b
    Examples:
      python cli.py order --symbol BTCUSDT --side BUY --type MARKET --quantity 0.001
      python cli.py order --symbol BTCUSDT --side BUY --type LIMIT --quantity 0.001 --price 50000
      python cli.py order --symbol ETHUSDT --side SELL --type STOP_LIMIT --quantity 0.01 --price 3000 --stop-price 3100
    """
    logger = ctx.obj["logger"]

    # ── Step 1: Validate inputs ──────────────────────────────────────
    try:
        symbol = validate_symbol(symbol)
        side = validate_side(side)
        order_type = validate_order_type(order_type)
        quantity = validate_quantity(quantity)

        price_required = order_type in ("LIMIT", "STOP_LIMIT")
        price = validate_price(price, required=price_required)

        stop_price_required = order_type == "STOP_LIMIT"
        stop_price = validate_stop_price(stop_price, required=stop_price_required)
    except ValueError as exc:
        click.secho(f"\n  ❌ Validation error: {exc}", fg="red", bold=True)
        click.echo()
        sys.exit(1)

    # ── Step 2: Print order summary ──────────────────────────────────
    _print_order_summary(symbol, side, order_type, quantity, price, stop_price)

    # ── Step 3: Confirm with user ────────────────────────────────────
    if not yes:
        if not click.confirm("  Proceed with this order?", default=False):
            click.secho("\n  ⛔ Order cancelled by user.", fg="yellow")
            sys.exit(0)
        click.echo()

    # ── Step 4: Initialize client & place order ──────────────────────
    api_key = os.getenv("BINANCE_TESTNET_API_KEY")
    api_secret = os.getenv("BINANCE_TESTNET_API_SECRET")

    try:
        with BinanceTestnetClient(api_key, api_secret) as client:
            if order_type == "MARKET":
                result = place_market_order(client, symbol, side, quantity)
            elif order_type == "LIMIT":
                result = place_limit_order(client, symbol, side, quantity, price)
            elif order_type == "STOP_LIMIT":
                result = place_stop_limit_order(
                    client, symbol, side, quantity, price, stop_price
                )
            else:
                # Should never reach here thanks to validation
                click.secho(f"\n  ❌ Unsupported order type: {order_type}", fg="red")
                sys.exit(1)

    except ValueError as exc:
        click.secho(f"\n  ❌ Configuration error: {exc}", fg="red", bold=True)
        logger.error("Configuration error: %s", exc)
        sys.exit(1)
    except BinanceAPIError as exc:
        click.secho(f"\n  ❌ Binance API error: {exc}", fg="red", bold=True)
        logger.error("Binance API error: %s", exc)
        sys.exit(1)
    except Exception as exc:
        click.secho(f"\n  ❌ Unexpected error: {exc}", fg="red", bold=True)
        logger.exception("Unexpected error during order placement")
        sys.exit(1)

    # ── Step 5: Print formatted response ─────────────────────────────
    _print_order_result(result)

    click.secho(
        "  📝 Full details logged to: logs/trading_bot.log",
        fg="cyan",
    )
    click.echo()


# ── Entry point ──────────────────────────────────────────────────────

if __name__ == "__main__":
    cli()
