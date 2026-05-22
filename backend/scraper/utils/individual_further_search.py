import sys
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from nltk.sentiment.vader import SentimentIntensityAnalyzer
from datetime import datetime, timedelta


def format_time(raw_time):
    time_parts = raw_time.split()

    # ',' means date is in format 'month day, a previous year'
    if "," in raw_time:
        return None

    if "hour" in time_parts or "hours" in time_parts or "minutes" in time_parts:
        published_date = datetime.now()
    elif "Yesterday" in time_parts:
        published_date = datetime.now() - timedelta(days=1)
    elif "days" in time_parts:
        days = int(time_parts[0])
        published_date = datetime.now() - timedelta(days=days)
    else:
        try:
            published_date = datetime.strptime(
                raw_time + f" {datetime.now().year}", "%b %d %Y"
            ).date()
        except ValueError:
            return None

    return published_date


def individual_further_search(ticker):
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    browser = webdriver.Chrome(options=chrome_options)

    url = f"https://news.google.com/search?q={ticker}"
    browser.get(url)

    browser.implicitly_wait(10)

    for i in range(10):
        # Scroll down to the bottom of the page
        browser.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        browser.implicitly_wait(2)

    browser.implicitly_wait(3)

    html = browser.page_source
    soup = BeautifulSoup(html, "html.parser")
    news_items = soup.find_all("c-wiz", {"jsrenderer": "ARwRbe"})

    browser.quit()

    sentiment_data = {ticker: {}}

    vader = SentimentIntensityAnalyzer()

    for item in news_items:
        title_tag = item.find(class_="JtKRv")
        time_tag = item.find(class_="hvbAAd")

        if not title_tag or not time_tag:
            continue

        title = title_tag.text
        date = format_time(time_tag.text)

        if not date:
            continue

        date = date.strftime("%Y-%m-%d")

        sentiment_score = vader.polarity_scores(title)["compound"]

        if date not in sentiment_data[ticker]:
            sentiment_data[ticker][date] = []

        sentiment_data[ticker][date].append(sentiment_score)

    return sentiment_data


if __name__ == "__main__":
    ticker = sys.argv[1]
    individual_further_search(ticker)
