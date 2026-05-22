# Architecture

## Main Components

### Frontend (React / Vite)

| File | Responsibility |
|------|---------------|
| `App.jsx` | Top-level router. Single route (`/`) renders `Home`. Configures `react-hot-toast` for error notifications. |
| `Home.jsx` | Fetches top-5 tickers and all stored sentiment data. Renders a 7-day grouped bar chart (Recharts `BarChart`) and a ranked table of the top 5 stocks. |
| `TickerSearch.jsx` | Ticker search form. On submit, POSTs to `/start-individual-scraper`, then renders two line charts side by side: sentiment score history and stock price history (past 7 trading days). |
| `GlobalStyle.js`, `Layout.js` | Shared styled-components for page layout and global CSS resets. |

Key frontend libraries: `axios` (HTTP), `recharts` (charts), `styled-components` (CSS-in-JS), `date-fns` (date formatting), `react-hot-toast` (toast notifications).

### Backend (Flask)

| Module | Responsibility |
|--------|---------------|
| `app.py` | Flask application entry point. Defines the `Sentiment` SQLAlchemy model, REST endpoints, APScheduler cron job, and response caching. |
| `scraper/top_5_scraper.py` | Batch scraper. Gets the top 5 tickers by market cap, scrapes Yahoo Finance news for each, scores headlines with VADER, averages scores per date, and POSTs results to `/sentiments`. Falls back to Google News via `further_search` when Yahoo coverage is insufficient. |
| `scraper/utils/get_top_5_stocks_by_marketcap.py` | Scrapes Finviz screener (sorted by descending market cap) to return the top 5 unique tickers and company names. |
| `scraper/utils/get_prices.py` | Scrapes Yahoo Finance historical prices page for a ticker using Selenium. Returns a list of `(ticker, date, close_price)` tuples. |
| `scraper/utils/get_individual_data.py` | Scrapes Yahoo Finance news for a single ticker, scores headlines, merges with Google News fallback data from `individual_further_search`, and returns aggregated sentiment data (not persisted to DB). |
| `scraper/utils/further_search.py` | Google News fallback for the top-5 batch scraper. Scrapes, scores, and POSTs results to the API. Used when Yahoo coverage spans less than 8 days. |
| `scraper/utils/individual_further_search.py` | Google News fallback for the individual ticker flow. Same logic as `further_search` but returns data in-memory instead of POSTing it. |
| `scraper/utils/format_time.py` | Parses relative time strings from Yahoo Finance (e.g., "2 days ago", "Yesterday") into `datetime` objects. |
| `scraper/utils/is_valid_ticker.py` | Validates a ticker by loading its Yahoo Finance page in Selenium and checking whether the URL redirects to an error page. |

### Database (MySQL)

Single table via SQLAlchemy:

```
Sentiment
  id              INTEGER   PRIMARY KEY
  ticker          VARCHAR(10)
  date            DATE
  sentiment_score FLOAT
```

Uniqueness is enforced at the application level: the `/sentiments` POST handler checks for existing rows with the same ticker and date before inserting.

## API Endpoints

| Method | Path | Description | Caching |
|--------|------|-------------|---------|
| GET | `/sentiments` | Return all sentiment records, optionally filtered by `?ticker=` query param. | None |
| POST | `/sentiments` | Insert or update a sentiment record. Rejects duplicates unless the existing score is 0. | None |
| GET | `/top-5-stocks` | Return top 5 tickers and company names by market cap (scraped from Finviz). | 1-hour SimpleCache |
| POST | `/start-top-5-scraper` | Trigger the top-5 batch scraper in a subprocess. | None |
| POST | `/start-individual-scraper` | Validate ticker, scrape prices and sentiment for it, return results directly (not persisted). | None |

## Data Flow

### Top-5 Daily Scrape (batch, scheduled or manual)

```
APScheduler (midnight cron) or POST /start-top-5-scraper
  --> subprocess: python scraper/top_5_scraper.py
      --> get_top_5_stocks_by_marketcap()  [Finviz]
      --> for each ticker:
            Selenium --> Yahoo Finance /quote/{ticker}/news
            BeautifulSoup --> extract headlines + timestamps
            VADER --> score each headline
            average scores per date
            if coverage < 8 days:
                further_search() --> Google News --> score + POST /sentiments
            POST /sentiments for each date
```

### Individual Ticker Search (on-demand, synchronous)

```
POST /start-individual-scraper { ticker }
  --> is_valid_ticker()       [Selenium --> Yahoo Finance]
  --> get_prices()            [Selenium --> Yahoo Finance /quote/{ticker}/history]
  --> get_individual_data()   [Selenium --> Yahoo Finance /quote/{ticker}/news]
      --> if coverage < 11 days:
            individual_further_search() --> Google News
      --> merge + average scores
  --> return { prices, sentiment_data } to frontend
```

### Frontend Display

```
Page load:
  GET /top-5-stocks  --> populate table + chart legend
  GET /sentiments    --> populate 7-day bar chart

Ticker search submit:
  POST /start-individual-scraper --> render sentiment line chart + price line chart
```

## External Dependencies

| Service | Used For | Access Method |
|---------|----------|---------------|
| Yahoo Finance | News headlines, historical prices, ticker validation | Selenium (headless Chrome) + BeautifulSoup |
| Google News | Fallback news headlines when Yahoo coverage is thin | Selenium (headless Chrome) + BeautifulSoup |
| Finviz | Top 5 stocks by market cap | HTTP request (urllib) + BeautifulSoup |

## Design Rationale

- **Subprocess for batch scraper**: The top-5 scraper is launched via `subprocess.Popen` so the Flask process is not blocked during the long-running Selenium scrape cycle. The scraper communicates results back by POSTing to the Flask API.
- **Two separate Google News fallback modules**: The batch flow (`further_search`) POSTs results directly to the database via the API, while the individual flow (`individual_further_search`) returns data in-memory so it can be merged and sent in a single response. This separation avoids persisting individual search results that the user may not want stored.
- **SimpleCache for top-5 endpoint**: Since the top 5 stocks by market cap rarely change within an hour, caching avoids repeated Finviz scrapes on every page load.
- **Single-table schema**: Sentiment data has a simple structure (ticker, date, score). A single table keeps the schema minimal and avoids join overhead.
