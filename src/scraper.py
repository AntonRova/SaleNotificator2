import re
import requests
from bs4 import BeautifulSoup
from typing import Optional


class PriceScraper:
    """Scrapes prices from product pages."""

    HEADERS = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
    }

    def __init__(self, timeout: int = 30):
        self.timeout = timeout

    def fetch_page(self, url: str) -> Optional[str]:
        """Fetch the HTML content of a page."""
        try:
            response = requests.get(url, headers=self.HEADERS, timeout=self.timeout)
            response.raise_for_status()
            return response.text
        except requests.RequestException as e:
            raise ScraperError(f"Failed to fetch {url}: {e}")

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
