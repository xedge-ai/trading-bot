# Binance Futures Testnet Trading Bot

A lightweight Python CLI app to place orders on **Binance Futures Testnet (USDT-M)**. Supports Market, Limit, and Stop-Market orders with structured logging, input validation, and clean error handling.

---

## Project Structure

```
trading_bot/
├── bot/
│   ├── __init__.py
│   ├── client.py          # Binance REST API wrapper (signing, HTTP)
│   ├── orders.py          # Order placement logic + output formatting
│   ├── validators.py      # Input validation helpers
│   └── logging_config.py  # Logger setup (file + console)
├── logs/
│   └── trading_YYYYMMDD.log
├── cli.py                 # CLI entry point (argparse)
├── .env.example
├── requirements.txt
└── README.md
```

---

## Setup

### 1. Get Testnet Credentials

1. Go to [https://testnet.binancefuture.com](https://testnet.binancefuture.com)
2. Log in with your GitHub account
3. Click **API Key** in the top-right menu
4. Copy your API key and secret

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

> Requires Python 3.8+

### 3. Configure Credentials

```bash
cp .env.example .env
```

Edit `.env`:
```
BINANCE_API_KEY=your_api_key_here
BINANCE_API_SECRET=your_api_secret_here
```

Alternatively, pass them inline via `--api-key` / `--api-secret` flags.

---

## How to Run

### Place a Market Order

```bash
# Market BUY — 0.01 BTC
python cli.py --symbol BTCUSDT --side BUY --type MARKET --quantity 0.01

# Market SELL — 0.05 ETH
python cli.py --symbol ETHUSDT --side SELL --type MARKET --quantity 0.05
```

### Place a Limit Order

```bash
# Limit BUY at $90,000
python cli.py --symbol BTCUSDT --side BUY --type LIMIT --quantity 0.01 --price 90000

# Limit SELL at $3,500
python cli.py --symbol ETHUSDT --side SELL --type LIMIT --quantity 0.1 --price 3500
```

### Place a Stop-Market Order (Bonus)

```bash
# Stop-Market BUY — triggers when price hits $98,000
python cli.py --symbol BTCUSDT --side BUY --type STOP_MARKET --quantity 0.005 --stop-price 98000
```

### Pass Credentials Inline

```bash
python cli.py --symbol BTCUSDT --side BUY --type MARKET --quantity 0.01 \
  --api-key YOUR_KEY --api-secret YOUR_SECRET
```

### Help

```bash
python cli.py --help
```

---

## Sample Output

```
┌─────────────────────────────────┐
│         ORDER REQUEST           │
├─────────────────────────────────┤
│  Symbol     : BTCUSDT           │
│  Side       : BUY               │
│  Type       : MARKET            │
│  Quantity   : 0.01              │
└─────────────────────────────────┘

┌─────────────────────────────────┐
│         ORDER RESPONSE          │
├─────────────────────────────────┤
│  Order ID   : 4751283901        │
│  Status     : FILLED            │
│  Exec Qty   : 0.01              │
│  Avg Price  : 96742.50000       │
│  Symbol     : BTCUSDT           │
│  Side       : BUY               │
│  Type       : MARKET            │
└─────────────────────────────────┘

  Order placed successfully!
```

---

## Logging

Logs are written to `logs/trading_YYYYMMDD.log`.

- **Console**: INFO level and above
- **File**: DEBUG level and above (includes full request/response bodies)

Log entries cover:
- All API requests (endpoint, params, minus signature)
- All API responses (status, body excerpt)
- Validation errors
- API errors (code + message)
- Network failures

---

## Assumptions

- Only **USDT-M Futures Testnet** is targeted (`testnet.binancefuture.com`)
- Limit orders default to `timeInForce=GTC` (Good Till Cancelled)
- Symbols are automatically uppercased (e.g. `btcusdt` → `BTCUSDT`)
- Credentials can come from `.env`, environment variables, or CLI flags — in that order of priority
- The bot does **not** manage positions or leverage — it only places new orders

---

## Error Handling

| Scenario | Behaviour |
|---|---|
| Invalid side/type/symbol | Prints validation error, exits with code 1 |
| Missing price for LIMIT | Prints validation error, exits with code 1 |
| API error (e.g. insufficient margin) | Prints API error code + message, exits with code 1 |
| Network timeout/failure | Logs exception, prints error, exits with code 1 |
| Missing credentials | Prints clear message, exits with code 1 |

---

## Bonus Feature

**Stop-Market orders** are supported as a third order type via `--type STOP_MARKET --stop-price <value>`. This lets you place conditional orders that trigger when the market hits your stop price.
