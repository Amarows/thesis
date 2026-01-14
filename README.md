# Thesis Project: IBKR & Yahoo Finance Toolkit

A Python-based toolkit for automated financial data collection and analysis, specifically designed for Interaction with Interactive Brokers (IBKR) TWS/Gateway and Yahoo Finance.

## Overview

This project provides a set of tools to:
- Connect to Interactive Brokers via TWS or IB Gateway using the `ibapi`.
- Download historical price data (bars) for stocks and cryptocurrencies.
- Retrieve news headlines and full article bodies from IBKR news providers.
- Fetch market data, price targets, and FX rates from Yahoo Finance.
- Normalize and process financial data using `pandas`.

## Stack

- **Language:** Python 3.x
- **Core Libraries:**
  - `ibapi`: Interactive Brokers Python API.
  - `pandas`: Data manipulation and analysis.
  - `yfinance`: Yahoo Finance market data downloader.
  - `matplotlib`: Data visualization.
  - `requests`: HTTP requests (used in Web API experiments).

## Requirements

### Software
- **Interactive Brokers TWS or IB Gateway:** Must be running and configured to allow API connections.
- **Python 3.8+**

### API Configuration (TWS/Gateway)
1. Go to `Configuration` -> `API` -> `Settings`.
2. Enable "Enable ActiveX and Socket Clients".
3. Note the "Socket port" (default is `7496` for paper trading and `7497` for live trading).
4. Ensure "Read-Only API" is unchecked if you plan to place orders.

## Setup

1. **Clone the repository:**
   ```bash
   git clone <repository-url>
   cd thesis
   ```

2. **Install dependencies:**
   Currently, there is no `requirements.txt`. You can install the necessary packages via pip:
   ```bash
   pip install pandas yfinance matplotlib requests
   ```
   *Note: `ibapi` must be installed from the Interactive Brokers website or their official GitHub repository if not available via pip.*

3. **Configure Environment:**
   Update the connection settings (host, port, clientId) in `demo.py` or your custom scripts to match your TWS/Gateway setup.

## Usage

### Entry Points

- **`market_data_process.py`**: A script for estimations and simulations. It loads local market data and news from the `data/` folder, merging them into pandas time series for offline analysis.
- **`3_news_sentiment.py`**: Performs sentiment analysis on news headlines and aggregates sentiment scores by symbol and time.
- **`demo.py`**: The primary demonstration script. It connects to IBKR, downloads historical data for a list of symbols, plots normalized prices, and fetches recent news headlines.
  ```bash
  python demo.py
  ```

### Key Modules

- **`src_api_ibkr/`**:
  - `ibkr_tws_api.py`: Contains `TradingApp`, the core EClient/EWrapper implementation.
  - `historical_data_toolkit.py`: High-level functions for downloading and saving historical data to CSV.
  - `ibkr_news_toolkit.py`: Toolkit for fetching news headlines and articles.
  - `ibkr_webapi.py`: Experimental script for IBKR Client Portal Web API.

- **`src_api_yahoo/`**:
  - `market_data_toolkit.py`: Utilities for fetching prices, price targets, and FX rates from Yahoo Finance, with support for CHF normalization.

### Data Storage
- Downloaded data is stored in the `data/` directory by default in CSV format.

## Project Structure

```text
.
├── data/                       # Cached CSV data (prices, news)
├── src_api_ibkr/               # IBKR TWS API integration
│   ├── historical_data_toolkit.py
│   ├── ibkr_news_toolkit.py
│   ├── ibkr_tws_api.py
│   └── ibkr_webapi.py
├── src_api_yahoo/              # Yahoo Finance integration
│   └── market_data_toolkit.py
├── market_data_process.py      # Process and merge local data
├── 3_news_sentiment.py         # Sentiment analysis pipeline
├── demo.py                     # Main entry point / demonstration
├── drafts.py                   # Development drafts
├── research_plan.md            # Project documentation/plan
└── README.md                   # Project documentation
```

## Scripts

- `market_data_process.py`: Process and merge local price and news data for analysis.
- `3_news_sentiment.py`: Analyze sentiment from news and aggregate it.
- `demo.py`: Run this to verify your connection and data downloading.
- `drafts.py`: General scratchpad for new features.
- `research_plan.md`: A detailed Markdown document outlining the research objectives, hypotheses, survey design, and project plan.

## Env Vars
- Currently, no `.env` file is used. Configuration is handled within the scripts (e.g., `IBKRConnectionConfig`).

## Tests
- [TODO: Add information about testing suite or how to run tests]

## License
- [TODO: Add license information]
