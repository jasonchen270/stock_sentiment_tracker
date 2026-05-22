# Engineering Decisions

## 1. NLTK VADER for Sentiment Analysis

**Decision**: Use VADER (Valence Aware Dictionary and sEntiment Reasoner) from NLTK to score news headlines.

**Alternatives considered**:
- **FinBERT or other transformer-based models**: Higher accuracy on financial text, but requires GPU or significant CPU time, model downloads (~400 MB+), and more complex deployment.
- **TextBlob**: Similar simplicity to VADER but less well-suited to social media and headline-style text. VADER was specifically designed for short, informal text.
- **External sentiment APIs (e.g., Google NLP, AWS Comprehend)**: High accuracy, but adds cost per request and an external dependency.

**Reasoning**: VADER is lightweight, requires no training, runs instantly on CPU, and handles short opinionated text well. Headlines are typically 5-15 words with clear positive/negative signals, which plays to VADER's strengths. The compound score provides a single normalized metric (-1 to +1) that is easy to store and chart.

**Tradeoffs**: VADER does not understand financial domain language well (e.g., "short" as a bearish position vs. "short" as an adjective). It cannot detect sarcasm or nuanced context. Accuracy is lower than fine-tuned transformer models, but the simplicity and zero-cost tradeoff is acceptable for a personal project.

## 2. Selenium + BeautifulSoup for Web Scraping

**Decision**: Use Selenium with headless Chrome to load pages, then parse the rendered HTML with BeautifulSoup.

**Alternatives considered**:
- **Plain HTTP requests (requests/urllib) + BeautifulSoup**: Faster and lighter, but Yahoo Finance and Google News render news content via JavaScript. Static HTML requests return incomplete pages.
- **Official APIs (Yahoo Finance API, NewsAPI, Google News RSS)**: More reliable and structured data. However, Yahoo Finance deprecated its free API, NewsAPI free tier is limited, and Google News RSS does not provide the same coverage as the full page.
- **Playwright or Puppeteer**: Modern alternatives to Selenium with better async support. Selenium was chosen for its mature Python ecosystem and wide documentation.

**Reasoning**: The target sites rely heavily on client-side JavaScript rendering. Selenium is the most straightforward way to get fully rendered HTML in Python. BeautifulSoup provides a simple API for extracting specific elements once the HTML is available.

**Tradeoffs**: Selenium is slow (each page load takes several seconds, plus scrolling delays). It requires a Chrome/Chromium installation. Scraping is inherently fragile -- any change to the target site's HTML class names or structure will break the parser. The application has no retry logic or graceful degradation when scraping fails.

## 3. Google News as a Fallback Source

**Decision**: When Yahoo Finance does not provide enough recent articles (less than ~8 days for batch, ~11 days for individual), supplement with Google News results.

**Alternatives considered**:
- **Yahoo Finance only**: Simpler, single source, but sometimes yields insufficient data for a full 7-day chart.
- **Always scrape both sources**: More data, but doubles scraping time and may introduce duplicate or conflicting sentiment signals for the same underlying news story.
- **Use a news aggregation API**: Would provide broader coverage with less code, but adds cost and an external dependency.

**Reasoning**: Yahoo Finance is the primary source because its news pages are ticker-specific and high quality. Google News is a good fallback because it has broad coverage and can be searched by ticker symbol. The conditional trigger (checking whether the last scraped date is recent enough) avoids unnecessary Google News scrapes when Yahoo coverage is sufficient.

**Tradeoffs**: Google News results are not ticker-specific in the same way -- a search for "AAPL" may return tangentially related articles. The two sources use different HTML structures, requiring separate parsing code (`further_search.py` and `individual_further_search.py`). There is also a risk of double-counting sentiment if the same story appears on both sites.

## 4. Subprocess-Based Scraper Execution

**Decision**: The batch scraper (`top_5_scraper.py`) is launched as a subprocess via `subprocess.Popen` rather than running inline within the Flask request handler.

**Alternatives considered**:
- **Run scraper inline in the request handler**: Simpler code, but the scraper takes minutes to complete (multiple Selenium sessions, scrolling, network requests). This would block the Flask worker and cause HTTP timeouts.
- **Celery or RQ task queue**: Purpose-built for background tasks, with retry logic, result tracking, and scalability. Adds infrastructure complexity (Redis/RabbitMQ broker).
- **Python threading**: Lighter than a subprocess, but Selenium is not thread-safe and the GIL limits true parallelism.

**Reasoning**: `subprocess.Popen` is the simplest way to run a long task without blocking Flask. The scraper communicates results by POSTing back to the API, so no shared memory or IPC mechanism is needed. For a single-user application, this approach is sufficient.

**Tradeoffs**: There is no visibility into whether the subprocess succeeded or failed. No retry logic. No way for the frontend to track scraper progress. If the Flask server restarts, in-flight scraper subprocesses are orphaned. A task queue would solve all of these problems but at the cost of additional infrastructure.

## 5. 1-Hour Response Cache on Top-5 Endpoint

**Decision**: Use Flask-Caching with `SimpleCache` (in-memory, single-process) and a 3600-second TTL on the `/top-5-stocks` endpoint.

**Alternatives considered**:
- **No caching**: Every page load triggers a Finviz scrape. Slow and risks rate limiting.
- **Redis or Memcached**: Production-grade caching with shared state across workers. Overkill for a single-process Flask dev server.
- **Longer TTL or database-backed cache**: Top 5 stocks by market cap change infrequently, so a longer TTL or storing the result in MySQL would also work.

**Reasoning**: The top 5 stocks by market cap do not change frequently (typically stable for days or weeks). Caching for 1 hour eliminates redundant Finviz requests during active use while still picking up changes within a reasonable window. `SimpleCache` requires zero configuration.

**Tradeoffs**: `SimpleCache` is in-process only -- it does not survive server restarts and does not work with multiple Gunicorn workers. Acceptable for local development but would need to be replaced with Redis for production deployment.
