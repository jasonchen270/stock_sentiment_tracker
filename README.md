# Stock Sentiment Tracker

A full-stack web app (React + Vite frontend, Flask backend with Selenium/BeautifulSoup scraping and NLTK VADER scoring, MySQL) that scrapes financial news, scores daily sentiment, and charts it against stock price history. The home page shows a 7-day sentiment bar chart for the top 5 stocks by market cap, and you can search any ticker to see its sentiment and price trends.

## Prerequisites

- Node 20+ and npm 10+
- Python 3.11+
- MySQL 8+

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
