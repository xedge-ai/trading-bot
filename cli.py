#!/usr/bin/env python3
"""
Binance Futures Testnet Trading Bot
CLI entry point
"""

import argparse
import os
import sys

from dotenv import load_dotenv

from bot.client import BinanceClient, BinanceClientError
from bot.logging_config import setup_logger
from bot.orders import format_order_response, format_order_summary, place_order, _build_order_params
from bot.validators import (
    ValidationError,
    validate_order_type,
    validate_price,
    validate_quantity,
    validate_side,
    validate_stop_price,
    validate_symbol,
)

load_dotenv()

logger = setup_logger("trading_bot.cli")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="trading_bot",
        description="Place orders on Binance Futures Testnet (USDT-M)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Market BUY
  python cli.py --symbol BTCUSDT --side BUY --type MARKET --quantity 0.01

  # Limit SELL
  python cli.py --symbol ETHUSDT --side SELL --type LIMIT --quantity 0.1 --price 3500

  # Stop-Market BUY
  python cli.py --symbol BTCUSDT --side BUY --type STOP_MARKET --quantity 0.01 --stop-price 70000
        """,
    )

    parser.add_argument("--symbol", required=True, help="Trading pair symbol, e.g. BTCUSDT")
    parser.add_argument("--side", required=True, help="BUY or SELL")
    parser.add_argument("--type", dest="order_type", required=True, help="MARKET, LIMIT, or STOP_MARKET")
    parser.add_argument("--quantity", required=True, help="Order quantity")
    parser.add_argument("--price", default=None, help="Limit price (required for LIMIT orders)")
    parser.add_argument("--stop-price", dest="stop_price", default=None, help="Stop price (required for STOP_MARKET)")
    parser.add_argument(
        "--api-key",
        default=None,
        help="Binance API key (or set BINANCE_API_KEY env var)",
    )
    parser.add_argument(
        "--api-secret",
        default=None,
        help="Binance API secret (or set BINANCE_API_SECRET env var)",
    )

    return parser


def resolve_credentials(args: argparse.Namespace):
    api_key = args.api_key or os.getenv("BINANCE_API_KEY")
    api_secret = args.api_secret or os.getenv("BINANCE_API_SECRET")

    if not api_key:
        print("ERROR: Binance API key not provided. Use --api-key or set BINANCE_API_KEY in .env")
        sys.exit(1)
    if not api_secret:
        print("ERROR: Binance API secret not provided. Use --api-secret or set BINANCE_API_SECRET in .env")
        sys.exit(1)

    return api_key, api_secret


def main():
    parser = build_parser()
    args = parser.parse_args()

    # --- Validate inputs ---
    try:
        symbol = validate_symbol(args.symbol)
        side = validate_side(args.side)
        order_type = validate_order_type(args.order_type)
        quantity = validate_quantity(args.quantity)
        price = validate_price(args.price, order_type)
        stop_price = validate_stop_price(args.stop_price, order_type)
    except ValidationError as e:
        logger.error("Input validation failed: %s", e)
        print(f"\n[VALIDATION ERROR] {e}\n")
        parser.print_help()
        sys.exit(1)

    # --- Resolve API credentials ---
    api_key, api_secret = resolve_credentials(args)

    # --- Build and print order summary ---
    order_params = _build_order_params(
        symbol=symbol,
        side=side,
        order_type=order_type,
        quantity=quantity,
        price=price,
        stop_price=stop_price,
    )
    print(format_order_summary(order_params))

    # --- Place order ---
    client = BinanceClient(api_key=api_key, api_secret=api_secret)

    try:
        response = place_order(
            client=client,
            symbol=symbol,
            side=side,
            order_type=order_type,
            quantity=quantity,
            price=price,
            stop_price=stop_price,
        )
    except BinanceClientError as e:
        logger.error("Order placement failed (API error): %s", e)
        print(f"\n[API ERROR] {e}\n")
        sys.exit(1)
    except Exception as e:
        logger.exception("Unexpected error during order placement")
        print(f"\n[ERROR] Unexpected error: {e}\n")
        sys.exit(1)

    # --- Print response ---
    print(format_order_response(response))
    print("\nOrder placed successfully!\n")


if __name__ == "__main__":
    main()
