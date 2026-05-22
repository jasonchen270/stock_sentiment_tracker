import asyncio
import aiohttp
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from nltk.sentiment.vader import SentimentIntensityAnalyzer
from utils import get_top_5_stocks_by_marketcap, format_time, further_search
from datetime import datetime, timedelta


async def get_sentiment_data():
    tickers = get_top_5_stocks_by_marketcap()[0]

    news = {}

    chrome_options = Options()
    chrome_options.add_argument("--headless")
    browser = webdriver.Chrome(options=chrome_options)

    for ticker in tickers:
        url = f"https://finance.yahoo.com/quote/{ticker}/news"
        browser.get(url)

        browser.implicitly_wait(10)

        for i in range(10):
            # Scroll down to the bottom of the page
            browser.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            browser.implicitly_wait(2)

        browser.implicitly_wait(3)

        html = browser.page_source
        soup = BeautifulSoup(html, "html.parser")
        news_items = soup.find_all("li", class_="stream-item")
        news[ticker] = news_items

    browser.quit()

    sentiment_data = {ticker: {} for ticker in tickers}

    vader = SentimentIntensityAnalyzer()

    async with aiohttp.ClientSession() as session:
        for ticker, news_items in news.items():
            last_date = None

            for item in news_items:
                title_tag = item.find("h3")
                time_tag = item.find("div", class_="publishing")

                if not title_tag or not time_tag:
                    continue

                title = title_tag.text
                date = format_time(time_tag.text)

                if not date:
                    continue

                last_date = date

                date = date.strftime("%Y-%m-%d")

                sentiment_score = vader.polarity_scores(title)["compound"]

                if date not in sentiment_data[ticker]:
                    sentiment_data[ticker][date] = []

                sentiment_data[ticker][date].append(sentiment_score)

            if datetime.now().date() - last_date.date() < timedelta(days=8):
                await further_search(ticker)

        for ticker in sentiment_data:
            for date in sentiment_data[ticker]:
                scores = sentiment_data[ticker][date]
                mean_score = sum(scores) / len(scores)
                sentiment_data[ticker][date] = mean_score

                data = {"ticker": ticker, "date": date, "sentiment_score": mean_score}

                async with session.post(
                    "http://localhost:5000/sentiments", json=data
                ) as response:
                    print("Status code:", response.status)


if __name__ == "__main__":
    asyncio.run(get_sentiment_data())
