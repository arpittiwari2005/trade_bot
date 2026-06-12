# 🤖 Binance Futures Testnet Trading Bot

A Python CLI application for placing **Market**, **Limit**, and **Stop-Limit** orders on [Binance Futures Testnet](https://testnet.binancefuture.com) (USDT-M).

Built with clean architecture, structured logging, and comprehensive input validation.

---

## 📋 Features

- **Three order types**: Market, Limit, and Stop-Limit (bonus)
- **Both sides**: BUY and SELL
- **Input validation**: Symbol format, side, order type, quantity, and price checks
- **Structured logging**: Rotating file logs (DEBUG) + clean console output (INFO)
- **Error handling**: API errors, network failures, and invalid input
- **Enhanced CLI UX**: Colored output, order confirmation prompts, help text

---

## 🚀 Setup

### Prerequisites

- **Python 3.10+**
- A **Binance Futures Testnet** account with API credentials
  → Register at: https://testnet.binancefuture.com

### Installation

```bash
# 1. Clone the repository
git clone (https://github.com/arpittiwari2005/trade_bot)
cd trading_bot

# 2. Create and activate a virtual environment
python3 -m venv .venv
source .venv/bin/activate  # macOS/Linux
# .venv\Scripts\activate   # Windows

# 3. Install dependencies
pip install -r requirements.txt

# 4. Configure API credentials
cp .env.example .env
# Edit .env and add your Binance Testnet API key and secret
```

---

## 🎯 Usage

### General Syntax

```bash
python cli.py [--verbose] order --symbol SYMBOL --side SIDE --type TYPE --quantity QTY [--price PRICE] [--stop-price STOP_PRICE] [--yes]
```

### Place a Market Order

```bash
python cli.py order --symbol BTCUSDT --side BUY --type MARKET --quantity 0.001
```

### Place a Limit Order

```bash
python cli.py order --symbol BTCUSDT --side BUY --type LIMIT --quantity 0.001 --price 50000
```

### Place a Stop-Limit Order (Bonus)

```bash
python cli.py order --symbol ETHUSDT --side SELL --type STOP_LIMIT --quantity 0.01 --price 3000 --stop-price 3100
```

### Skip Confirmation Prompt

```bash
python cli.py order --symbol BTCUSDT --side BUY --type MARKET --quantity 0.001 --yes
```

### Enable Verbose (DEBUG) Logging

```bash
python cli.py --verbose order --symbol BTCUSDT --side BUY --type MARKET --quantity 0.001
```

### View Help

```bash
python cli.py --help
python cli.py order --help
```

---

## 📂 Project Structure

```
trading_bot/
├── bot/
│   ├── __init__.py          # Package init, version metadata
│   ├── client.py            # Binance API client (signing, HTTP, logging)
│   ├── orders.py            # Order placement logic (Market, Limit, Stop-Limit)
│   ├── validators.py        # Input validation helpers
│   └── logging_config.py    # Structured logging configuration
├── cli.py                   # CLI entry point (Click-based)
├── logs/                    # Log files (auto-created)
│   ├── market_order.log     # Sample log: Market order
│   └── limit_order.log      # Sample log: Limit order
├── .env.example             # Environment variable template
├── .gitignore
├── requirements.txt
└── README.md
```

### Architecture

| Layer | File | Responsibility |
|-------|------|---------------|
| **CLI** | `cli.py` | User interaction, input parsing, output formatting |
| **Business Logic** | `bot/orders.py` | Order assembly, response extraction |
| **API Client** | `bot/client.py` | Request signing, HTTP execution, error handling |
| **Validation** | `bot/validators.py` | Input normalization and validation |
| **Logging** | `bot/logging_config.py` | Dual-handler logging configuration |

---

## 📊 Sample Output

### Market Order

```
──────────────────────────────────────────────────
  📋 Order Request Summary
──────────────────────────────────────────────────
  Symbol:          BTCUSDT
  Side:            BUY
  Type:            MARKET
  Quantity:        0.001

  Proceed with this order? [y/N]: y

──────────────────────────────────────────────────
  ✅ Order Response
──────────────────────────────────────────────────
  Order ID:        1234567890
  Symbol:          BTCUSDT
  Side:            BUY
  Type:            MARKET
  Status:          FILLED
  Quantity:        0.001
  Executed Qty:    0.001
  Price:           0
  Avg Price:       104532.50

  ✅ Order filled successfully!

  📝 Full details logged to: logs/trading_bot.log
```

---

## 📝 Assumptions & Design Decisions

1. **Direct REST calls** over `python-binance`: Chose `httpx` for full control over request signing, error handling, and logging — avoids quirks and deprecation in the unofficial library.

2. **Click** for CLI: Provides built-in validation, help generation, and colored output out of the box.

3. **HMAC-SHA256 signing**: All authenticated requests are signed per [Binance API docs](https://developers.binance.com/docs/derivatives/usds-margined-futures/general-info) using timestamp + query string.

4. **Stop-Limit uses `STOP` type**: On Binance Futures, the `STOP` order type functions as a stop-limit (requires `price`, `stopPrice`, and `timeInForce`).

5. **No position/leverage management**: The bot focuses on order placement. Leverage and margin type should be configured via the Binance Testnet UI or extended in a future version.

6. **Testnet only**: The base URL is hardcoded to `https://testnet.binancefuture.com`. This bot should **never** be pointed at the production API without proper review.

7. **Credentials via `.env`**: API keys are loaded from a `.env` file (never committed to git) using `python-dotenv`.

---

## 🧪 Running Tests

```bash
# Verify module imports
python -c "from bot.client import BinanceTestnetClient; print('✓ client OK')"
python -c "from bot.validators import validate_symbol; print(validate_symbol('btcusdt'))"

# Verify CLI help
python cli.py --help
python cli.py order --help
```

---

## 📄 Log Files

Logs are written to `logs/trading_bot.log` with rotating file handlers (5 MB max, 3 backups).

Sample log files from test runs are included in the `logs/` directory:
- `market_order.log` — Log from a Market BUY order
- `limit_order.log` — Log from a Limit BUY order

---

## 📦 Dependencies

| Package | Version | Purpose |
|---------|---------|---------|
| `httpx` | ≥ 0.27.0 | HTTP client for API calls |
| `click` | ≥ 8.1.0 | CLI framework |
| `python-dotenv` | ≥ 1.0.0 | Load `.env` credentials |
