import sys
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import datetime


def get_prices(ticker):
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    browser = webdriver.Chrome(options=chrome_options)

    url = f"https://finance.yahoo.com/quote/{ticker}/history/"
    browser.get(url)

    browser.implicitly_wait(10)

    html = browser.page_source
    soup = BeautifulSoup(html, "html.parser")
    table = soup.find_all("tr", class_="svelte-ewueuo")

    data = []

    for item in table:
        i = item.find_all("td")

        if len(i) >= 4:
            date = i[0].text
            close_price = i[4].text

            date = datetime.datetime.strptime(date, "%b %d, %Y").strftime("%Y-%m-%d")

            data.append((ticker, date, close_price))

    browser.quit()
    return data


if __name__ == "__main__":
    ticker = sys.argv[1]
    get_prices(ticker)
