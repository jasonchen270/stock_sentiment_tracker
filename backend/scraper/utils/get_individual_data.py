import sys
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from nltk.sentiment.vader import SentimentIntensityAnalyzer
from . import format_time, individual_further_search
from datetime import datetime, timedelta


def get_individual_data(ticker):
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    browser = webdriver.Chrome(options=chrome_options)

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

    browser.quit()

    sentiment_data = {ticker: {}}

    vader = SentimentIntensityAnalyzer()

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

    if datetime.now().date() - last_date.date() < timedelta(days=11):
        further_sentiment_data = individual_further_search.individual_further_search(
            ticker
        )

        for date, scores in further_sentiment_data[ticker].items():
            if date not in sentiment_data[ticker]:
                sentiment_data[ticker][date] = []

            sentiment_data[ticker][date].extend(scores)

    for date in sentiment_data[ticker]:
        scores = sentiment_data[ticker][date]
        mean_score = sum(scores) / len(scores)
        sentiment_data[ticker][date] = mean_score

    return sentiment_data


if __name__ == "__main__":
    ticker = sys.argv[1]
    get_individual_data(ticker)
