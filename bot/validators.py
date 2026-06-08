from typing import Optional


VALID_SIDES = {"BUY", "SELL"}
VALID_ORDER_TYPES = {"MARKET", "LIMIT", "STOP_MARKET"}


class ValidationError(Exception):
    pass


def validate_symbol(symbol: str) -> str:
    s = symbol.strip().upper()
    if not s:
        raise ValidationError("Symbol cannot be empty.")
    if not s.isalpha():
        raise ValidationError(f"Symbol '{s}' looks invalid — should be letters only (e.g. BTCUSDT).")
    return s


def validate_side(side: str) -> str:
    s = side.strip().upper()
    if s not in VALID_SIDES:
        raise ValidationError(f"Side must be one of {VALID_SIDES}, got '{side}'.")
    return s


def validate_order_type(order_type: str) -> str:
    ot = order_type.strip().upper()
    if ot not in VALID_ORDER_TYPES:
        raise ValidationError(f"Order type must be one of {VALID_ORDER_TYPES}, got '{order_type}'.")
    return ot


def validate_quantity(quantity: str) -> float:
    try:
        qty = float(quantity)
    except (ValueError, TypeError):
        raise ValidationError(f"Quantity must be a number, got '{quantity}'.")
    if qty <= 0:
        raise ValidationError(f"Quantity must be positive, got {qty}.")
    return qty


def validate_price(price: Optional[str], order_type: str) -> Optional[float]:
    """Price is required only for LIMIT orders."""
    if order_type == "LIMIT":
        if price is None:
            raise ValidationError(f"Price is required for {order_type} orders.")
        try:
            p = float(price)
        except (ValueError, TypeError):
            raise ValidationError(f"Price must be a number, got '{price}'.")
        if p <= 0:
            raise ValidationError(f"Price must be positive, got {p}.")
        return p
    return None


def validate_stop_price(stop_price: Optional[str], order_type: str) -> Optional[float]:
    """Stop price required for STOP_MARKET orders."""
    if order_type == "STOP_MARKET":
        if stop_price is None:
            raise ValidationError("Stop price is required for STOP_MARKET orders.")
        try:
            sp = float(stop_price)
        except (ValueError, TypeError):
            raise ValidationError(f"Stop price must be a number, got '{stop_price}'.")
        if sp <= 0:
            raise ValidationError(f"Stop price must be positive, got {sp}.")
        return sp
    return None
