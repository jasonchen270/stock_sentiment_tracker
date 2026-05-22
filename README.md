# Stock Sentiment Tracker

## Problem and Motivation

Stock prices are influenced by public sentiment, but manually reading through dozens of news articles per ticker every day is impractical. Retail investors lack a quick way to gauge market sentiment for the stocks they care about without paying for expensive data feeds.

## Solution

A full-stack web application that automatically scrapes news headlines from Yahoo Finance and Google News, computes daily sentiment scores using NLTK VADER, and visualizes them alongside stock price history. The home page shows a 7-day sentiment bar chart for the top 5 stocks by market cap. Users can also search any valid ticker to see its sentiment and price trends on line charts.

## How It Works

1. **Scraping**: Selenium loads Yahoo Finance news pages (and Google News as a fallback) for each ticker, scrolling to load dynamic content. BeautifulSoup parses the rendered HTML to extract headline text and publish timestamps.
2. **Sentiment analysis**: Each headline is scored using NLTK VADER's compound metric (range -1 to +1). All scores for a given ticker and date are averaged into a single daily sentiment score.
3. **Storage**: Daily scores are POSTed to the Flask API and persisted in MySQL via SQLAlchemy. Duplicate entries for the same ticker/date are rejected unless the existing score is zero (placeholder), in which case it is updated.
4. **Scheduling**: APScheduler runs the top-5 scraper as a cron job at midnight daily, keeping the database current without manual intervention.
5. **Display**: The React frontend fetches sentiment data and top-5 tickers from the API, then renders bar charts (top 5) and line charts (individual search) using Recharts.

## Architecture Summary

```
Frontend (React/Vite, port 5173)
    |--- axios ---> Flask API (port 5000)
                        |--- SQLAlchemy ---> MySQL
                        |--- APScheduler ---> top_5_scraper.py
                        |--- Selenium/BS4 ---> Yahoo Finance, Google News, Finviz
```

- **Frontend**: React 18, Vite, Styled Components, Recharts, react-hot-toast for error feedback.
- **Backend**: Flask with Flask-CORS, Flask-Caching (SimpleCache, 1-hour TTL on top-5 endpoint), Flask-APScheduler.
- **Scraper**: Selenium (headless Chrome) for JS-rendered pages, BeautifulSoup for HTML parsing, aiohttp for async POST requests back to the API.
- **Data sources**: Yahoo Finance (news + price history), Google News (fallback for additional coverage), Finviz (top 5 by market cap).

See [docs/architecture.md](docs/architecture.md) for details.

## Key Engineering Decisions

- VADER for sentiment analysis: no training data or GPU needed, works well on short news headlines.
- Selenium over plain HTTP requests: Yahoo Finance and Google News render content via JavaScript, so a headless browser is required.
- Google News as a fallback source: if Yahoo Finance does not have enough recent articles (less than ~8-11 days of coverage), the scraper supplements with Google News results.
- 1-hour response cache on the top-5-stocks endpoint to avoid redundant Finviz scrapes.

See [docs/decisions.md](docs/decisions.md) for the full rationale and tradeoffs.

## Limitations

- Scraping is fragile: changes to Yahoo Finance, Google News, or Finviz HTML structure will break the parsers.
- VADER is a lexicon-based model. It does not understand context, sarcasm, or domain-specific financial language.
- The scraper runs synchronously per ticker (one Selenium session at a time for the top-5 flow), so a full scrape cycle is slow.
- Ticker validation uses a Selenium roundtrip to Yahoo Finance, adding latency to individual searches.
- No authentication or rate limiting on the API.

## Future Improvements

- Replace Selenium scraping with official APIs (e.g., Yahoo Finance API, NewsAPI) for reliability and speed.
- Use a finance-tuned sentiment model (e.g., FinBERT) for more accurate scoring.
- Add parallel scraping across tickers to reduce total scrape time.
- Add user authentication and per-user watchlists.
- Deploy with a production WSGI server (Gunicorn) and a proper caching backend (Redis).

---

## Description
A stock sentiment analysis tracker based on news scraped from Yahoo Finance and Google News. Easily view weekly sentiment scores for top stocks and search stock sentiments for individual tickers.

![home](https://github.com/jasonchen17/stock_sentiment_tracker/blob/main/screenshots/home.png?raw=true)

## Built With
- **Frontend**: React, Vite, Styled Components
- **Backend**: Flask, BeautifulSoup, Selenium, NLTK
- **Database**: MySQL

## Prerequisites
- Node
- npm
- Python
- MySQL

## Installation
1. **Clone the repository**
    ```bash
    git clone https://github.com/jasonchen17/stock_sentiment_tracker.git

    cd stock_sentiment_tracker
    ```

2. **Create a `.env` file in the `backend` directory**
- Make sure MySQL is running and add your connection URI
&nbsp;

    ```text
    SQLALCHEMY_DATABASE_URI=mysql://<username>:<password>@<hostname>:<port>/<database_name>
    ```

3. **Install backend dependencies**
    ```bash
    cd backend

  	# Setup virtual environment
  	python -m venv venv
  	venv\Scripts\activate

  	# Make sure you're using the Python interpreter from the virtual environment
    # Install necessary packages
  	pip install -r requirements.txt

  	# Install NLTK Vader
  	python
  	>>> import nltk
  	>>> nltk.download('vader_lexicon')
    >>> exit()
    ```

4. **Install frontend dependencies**
    ```bash
    cd frontend

    npm install
    ```

## Usage
1. **Start the backend server**
    ```bash
    cd backend

    python app.py
    ```

2. **Start the frontend application**
    ```bash
    cd frontend

    npm run dev
    ```

3. **Run the scraper for the top 5 stocks**
   ```bash
    cd backend

    python scraper/top_5_scraper.py
    ```

4. **Open your browser and go to [http://localhost:5173](http://localhost:5173) to view the application**
