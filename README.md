# Stock Sentiment Tracker

A full-stack web app that scrapes financial news, scores daily sentiment with
NLTK VADER, and charts it against stock price history. The home page shows a
7-day sentiment bar chart for the top 5 stocks by market cap, and you can search
any ticker to see its sentiment and price trends.

![home](https://github.com/jasonchen270/stock_sentiment_tracker/blob/main/screenshots/home.png?raw=true)

## Problem and Motivation

Stock prices are influenced by public sentiment, but manually reading through
dozens of news articles per ticker every day is impractical. Retail investors
lack a quick way to gauge market sentiment for the stocks they care about without
paying for expensive data feeds.

## How It Works

1. **Scraping**: Selenium loads Yahoo Finance news pages (and Google News as a fallback) for each ticker, scrolling to load dynamic content. BeautifulSoup parses the rendered HTML to extract headline text and publish timestamps.
2. **Sentiment analysis**: Each headline is scored using NLTK VADER's compound metric (range -1 to +1). All scores for a given ticker and date are averaged into a single daily sentiment score.
3. **Storage**: Daily scores are POSTed to the Flask API and persisted in MySQL via SQLAlchemy. Duplicate entries for the same ticker/date are rejected unless the existing score is zero (placeholder), in which case it is updated.
4. **Scheduling**: APScheduler runs the top-5 scraper as a cron job at midnight daily, keeping the database current without manual intervention.
5. **Display**: The React frontend fetches sentiment data and top-5 tickers from the API, then renders bar charts (top 5) and line charts (individual search) using Recharts.

## Built With

- **Frontend**: React, Vite, Styled Components, Recharts
- **Backend**: Flask, Selenium, BeautifulSoup, NLTK VADER, APScheduler
- **Database**: MySQL

## Prerequisites

- Node and npm
- Python 3
- MySQL

## Installation

1. **Clone the repository**
    ```bash
    git clone https://github.com/jasonchen270/stock_sentiment_tracker.git
    cd stock_sentiment_tracker
    ```

2. **Create a `.env` file in the `backend` directory**

   Make sure MySQL is running, then add your connection URI:
    ```text
    SQLALCHEMY_DATABASE_URI=mysql://<username>:<password>@<hostname>:<port>/<database_name>
    ```

3. **Install backend dependencies**
    ```bash
    cd backend

    # Set up a virtual environment
    python -m venv venv
    venv\Scripts\activate        # Windows
    source venv/bin/activate     # macOS/Linux

    # Install packages
    pip install -r requirements.txt

    # Download the NLTK VADER lexicon
    python -m nltk.downloader vader_lexicon
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

4. Open your browser to [http://localhost:5173](http://localhost:5173) to view the application.
