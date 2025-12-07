import re
import time
import warnings
import cloudscraper
from bs4 import BeautifulSoup
from typing import Optional
from requests.exceptions import RequestException
from urllib.parse import urlparse
from urllib3.exceptions import InsecureRequestWarning

# Suppress SSL warnings when verification is disabled
warnings.simplefilter('ignore', InsecureRequestWarning)


class PriceScraper:
    """Scrapes prices from product pages."""

    def __init__(self, timeout: int = 30, delay: float = 2.0):
        self.timeout = timeout
        self.delay = delay
        self.last_request_time = 0
        # cloudscraper automatically handles Cloudflare challenges
        # and sets appropriate headers
        self.session = cloudscraper.create_scraper(
            browser={
                'browser': 'chrome',
                'platform': 'windows',
                'desktop': True
            },
            delay=10  # Delay between solving challenges
        )
        # Disable SSL verification globally for this session
        self.session.verify = False

    def _rate_limit(self):
        """Ensure minimum delay between requests."""
        if self.last_request_time > 0:
            elapsed = time.time() - self.last_request_time
            if elapsed < self.delay:
                time.sleep(self.delay - elapsed)
        self.last_request_time = time.time()

    def fetch_page(self, url: str, retries: int = 3) -> Optional[str]:
        """Fetch the HTML content of a page with retry logic."""
        self._rate_limit()

        for attempt in range(retries):
            try:
                # On first attempt for a domain, visit homepage first to get cookies
                if attempt == 0:
                    parsed = urlparse(url)
                    homepage = f"{parsed.scheme}://{parsed.netloc}"
                    try:
                        self.session.get(homepage, timeout=self.timeout)
                        time.sleep(1)  # Brief pause after homepage visit
                    except:
                        pass  # Ignore homepage errors, try the actual URL anyway

                response = self.session.get(url, timeout=self.timeout)
                response.raise_for_status()
                return response.text

            except RequestException as e:
                if attempt < retries - 1:
                    # Exponential backoff
                    wait_time = (attempt + 1) * 2
                    time.sleep(wait_time)
                else:
                    raise ScraperError(f"Failed to fetch {url}: {e}")

        return None

    def extract_price(self, html: str, css_selector: str) -> Optional[float]:
        """Extract price from HTML using CSS selector."""
        soup = BeautifulSoup(html, 'lxml')

        # Try multiple selectors if comma-separated
        selectors = [s.strip() for s in css_selector.split(',')]

        for selector in selectors:
            elements = soup.select(selector)
            for element in elements:
                price = self._parse_price_text(element.get_text())
                if price is not None:
                    return price

                # Check for data-price attribute
                if element.has_attr('data-price'):
                    price = self._parse_price_text(element['data-price'])
                    if price is not None:
                        return price

        # Fallback: search for price patterns in script tags (for JS-rendered prices)
        price = self._extract_from_scripts(soup)
        if price is not None:
            return price

        return None

    def _parse_price_text(self, text: str) -> Optional[float]:
        """Parse a price string and return the numeric value."""
        if not text:
            return None

        # Remove currency symbols and whitespace
        cleaned = re.sub(r'[^\d.,]', '', text.strip())

        if not cleaned:
            return None

        # Handle different number formats
        # Format: 1,234.56 or 1.234,56 or 1234
        if ',' in cleaned and '.' in cleaned:
            # Determine which is decimal separator
            if cleaned.rfind(',') > cleaned.rfind('.'):
                # European format: 1.234,56
                cleaned = cleaned.replace('.', '').replace(',', '.')
            else:
                # US format: 1,234.56
                cleaned = cleaned.replace(',', '')
        elif ',' in cleaned:
            # Could be thousands separator or decimal
            parts = cleaned.split(',')
            if len(parts) == 2 and len(parts[1]) == 2:
                # Likely decimal: 123,45
                cleaned = cleaned.replace(',', '.')
            else:
                # Thousands separator: 1,234 or 12,345
                cleaned = cleaned.replace(',', '')

        try:
            return float(cleaned)
        except ValueError:
            return None

    def _extract_from_scripts(self, soup: BeautifulSoup) -> Optional[float]:
        """Try to extract price from JavaScript data in the page."""
        scripts = soup.find_all('script')

        # Common patterns for prices in JS
        patterns = [
            r'"price"\s*:\s*(\d+(?:\.\d+)?)',
            r"'price'\s*:\s*(\d+(?:\.\d+)?)",
            r'"Price"\s*:\s*(\d+(?:\.\d+)?)',
            r'price\s*=\s*["\']?(\d+(?:\.\d+)?)',
            r'data-price=["\']?(\d+(?:\.\d+)?)',
        ]

        for script in scripts:
            if script.string:
                for pattern in patterns:
                    match = re.search(pattern, script.string)
                    if match:
                        try:
                            return float(match.group(1))
                        except ValueError:
                            continue

        return None

    def get_price(self, url: str, css_selector: str) -> float:
        """Fetch a page and extract the price."""
        html = self.fetch_page(url)
        price = self.extract_price(html, css_selector)

        if price is None:
            raise ScraperError(f"Could not extract price from {url}")

        return price


class ScraperError(Exception):
    """Exception raised when scraping fails."""
    pass
