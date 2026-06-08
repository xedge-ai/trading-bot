from typing import Any, Dict, Optional

from bot.client import BinanceClient
from bot.logging_config import setup_logger

logger = setup_logger("trading_bot.orders")


def _build_order_params(
    symbol: str,
    side: str,
    order_type: str,
    quantity: float,
    price: Optional[float] = None,
    stop_price: Optional[float] = None,
    time_in_force: str = "GTC",
) -> Dict[str, Any]:
    params: Dict[str, Any] = {
        "symbol": symbol,
        "side": side,
        "type": order_type,
        "quantity": quantity,
    }

    if order_type == "LIMIT":
        if price is None:
            raise ValueError("Price is required for LIMIT orders.")
        params["price"] = price
        params["timeInForce"] = time_in_force

    elif order_type == "STOP_MARKET":
        if stop_price is None:
            raise ValueError("Stop price is required for STOP_MARKET orders.")
        params["stopPrice"] = stop_price

    return params


def place_order(
    client: BinanceClient,
    symbol: str,
    side: str,
    order_type: str,
    quantity: float,
    price: Optional[float] = None,
    stop_price: Optional[float] = None,
) -> Dict[str, Any]:
    """
    Places an order on Binance Futures Testnet.
    Returns the full API response dict.
    """
    params = _build_order_params(
        symbol=symbol,
        side=side,
        order_type=order_type,
        quantity=quantity,
        price=price,
        stop_price=stop_price,
    )

    logger.info(
        "Placing order | symbol=%s | side=%s | type=%s | qty=%s | price=%s | stopPrice=%s",
        symbol, side, order_type, quantity, price, stop_price,
    )

    response = client.post("/fapi/v1/order", params=params)

    logger.info(
        "Order placed successfully | orderId=%s | status=%s | executedQty=%s | avgPrice=%s",
        response.get("orderId"),
        response.get("status"),
        response.get("executedQty"),
        response.get("avgPrice"),
    )

    return response


def format_order_summary(params: Dict[str, Any]) -> str:
    """Human-readable summary of what we're about to send."""
    lines = [
        "",
        "┌─────────────────────────────────┐",
        "│         ORDER REQUEST           │",
        "├─────────────────────────────────┤",
        f"│  Symbol     : {params.get('symbol', 'N/A'):<17}│",
        f"│  Side       : {params.get('side', 'N/A'):<17}│",
        f"│  Type       : {params.get('type', 'N/A'):<17}│",
        f"│  Quantity   : {str(params.get('quantity', 'N/A')):<17}│",
    ]
    if "price" in params:
        lines.append(f"│  Price      : {str(params.get('price')):<17}│")
    if "stopPrice" in params:
        lines.append(f"│  Stop Price : {str(params.get('stopPrice')):<17}│")
    lines.append("└─────────────────────────────────┘")
    return "\n".join(lines)


def format_order_response(response: Dict[str, Any]) -> str:
    """Human-readable order response."""
    lines = [
        "",
        "┌─────────────────────────────────┐",
        "│         ORDER RESPONSE          │",
        "├─────────────────────────────────┤",
        f"│  Order ID   : {str(response.get('orderId', 'N/A')):<17}│",
        f"│  Status     : {response.get('status', 'N/A'):<17}│",
        f"│  Exec Qty   : {str(response.get('executedQty', 'N/A')):<17}│",
        f"│  Avg Price  : {str(response.get('avgPrice', 'N/A')):<17}│",
        f"│  Symbol     : {response.get('symbol', 'N/A'):<17}│",
        f"│  Side       : {response.get('side', 'N/A'):<17}│",
        f"│  Type       : {response.get('type', 'N/A'):<17}│",
        "└─────────────────────────────────┘",
    ]
    return "\n".join(lines)
