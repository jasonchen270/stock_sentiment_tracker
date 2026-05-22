import subprocess
import os
from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from datetime import datetime
from flask_caching import Cache
from scraper.utils import (
    get_prices,
    get_top_5_stocks_by_marketcap,
    is_valid_ticker,
    get_individual_data,
)
from dotenv import load_dotenv
from flask_apscheduler import APScheduler

app = Flask(__name__)

CORS(app)

load_dotenv()

app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("SQLALCHEMY_DATABASE_URI")

db = SQLAlchemy(app)

cache = Cache(app, config={"CACHE_TYPE": "SimpleCache"})

scheduler = APScheduler()
scheduler.init_app(app)
scheduler.start()


class Sentiment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    ticker = db.Column(db.String(10), nullable=False)
    date = db.Column(db.Date, nullable=False)
    sentiment_score = db.Column(db.Float, nullable=False)

    def __init__(self, ticker, date, sentiment_score):
        self.ticker = ticker
        self.date = date
        self.sentiment_score = sentiment_score


def run_scheduled_top_5_scraper():
    command = "python scraper/top_5_scraper.py"
    subprocess.Popen(command, shell=True)
    app.logger.info("Scheduled scraper started successfully")


# Run scraper at 12:00 AM every day
@scheduler.task('cron', id='scheduled_top_5_scraper', hour=0)
def scheduled_top_5_scraper():
    with app.app_context():
        run_scheduled_top_5_scraper()


@app.route("/start-top-5-scraper", methods=["POST"])
def start_top_5_scraper():
    command = "python scraper/top_5_scraper.py"
    subprocess.Popen(command, shell=True)

    return jsonify({"message": "Scraper started successfully"}), 200


@app.route("/sentiments", methods=["POST"])
def submit_sentiment():
    data = request.json

    existing_sentiment = Sentiment.query.filter_by(
        ticker=data.get("ticker"), date=datetime.strptime(data.get("date"), "%Y-%m-%d")
    ).first()

    if existing_sentiment:
        if existing_sentiment.sentiment_score != 0:
            return (
                jsonify(
                    {
                        "message": "Sentiment data already exists for the given ticker and date"
                    }
                ),
                400,
            )
        else:
            existing_sentiment.sentiment_score = data.get("sentiment_score")
            db.session.commit()
            return jsonify({"message": "Sentiment data updated successfully"}), 200

    sentiment = Sentiment(
        ticker=data.get("ticker"),
        date=datetime.strptime(data.get("date"), "%Y-%m-%d"),
        sentiment_score=data.get("sentiment_score"),
    )

    db.session.add(sentiment)
    db.session.commit()

    return jsonify({"message": "Sentiment data added successfully"}), 200


@app.route("/sentiments", methods=["GET"])
def get_sentiments():
    ticker = request.args.get("ticker")

    if ticker:
        sentiments = Sentiment.query.filter_by(ticker=ticker).all()
    else:
        sentiments = Sentiment.query.all()

    result = []

    for sentiment in sentiments:
        result.append(
            {
                "ticker": sentiment.ticker,
                "date": sentiment.date.strftime("%Y-%m-%d"),
                "sentiment_score": sentiment.sentiment_score,
            }
        )

    return jsonify(result), 200


@app.route("/top-5-stocks", methods=["GET"])
@cache.cached(timeout=3600)
def top_5_stocks():
    tickers = get_top_5_stocks_by_marketcap()
    return jsonify({"top_5_stocks": tickers}), 200


@app.route("/start-individual-scraper", methods=["POST"])
def start_individual_scraper():
    ticker = request.json.get("ticker")

    if not ticker or not is_valid_ticker(ticker):
        return jsonify({"message": "Invalid ticker"}), 400

    prices = get_prices(ticker)

    if not prices:
        return jsonify({"message": "Failed to retrieve price data"}), 500

    sentiment_data = get_individual_data(ticker)

    if not sentiment_data:
        return jsonify({"message": "Failed to retrieve sentiment data"}), 500

    return jsonify({"prices": prices, "sentiment_data": sentiment_data}), 200


if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)
