import sys
from selenium import webdriver
from selenium.webdriver.chrome.options import Options


def is_valid_ticker(ticker):
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    browser = webdriver.Chrome(options=chrome_options)

    url = f"https://finance.yahoo.com/quote/{ticker}/news"
    browser.get(url)

    browser.implicitly_wait(10)

    if "err" in browser.current_url:
        return False
    else:
        return True


if __name__ == "__main__":
    ticker = sys.argv[1]
    is_valid_ticker(ticker)
