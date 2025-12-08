#!/usr/bin/env python3
"""
Amazon Price Selector Finder

This script helps you find the correct CSS selector for an Amazon product price.
Run it and it will show you all prices found on the page and their selectors.
"""

import sys
sys.path.insert(0, 'src')

from scraper import PriceScraper
from bs4 import BeautifulSoup

# Your Amazon product URL
url = "https://www.amazon.com/JONSBO-Supports-Built-Veneer-Computer/dp/B0DG2N3PBB"

print("Fetching Amazon page...")
print("="*70)

scraper = PriceScraper()
html = scraper.fetch_page(url)

print(f"✓ Fetched {len(html):,} bytes\n")

soup = BeautifulSoup(html, 'lxml')

# Test multiple Amazon price selectors
selectors_to_test = [
    # Main price area
    ('.a-price .a-offscreen', 'All prices (offscreen)'),
    ('#corePriceDisplay_desktop_feature_div .a-price .a-offscreen', 'Core price display'),
    ('#apex_desktop .a-price .a-offscreen', 'Apex desktop price'),

    # Specific price types
    ('span.a-price[data-a-color="price"] .a-offscreen', 'Main colored price'),
    ('.a-price.aok-align-center .a-offscreen', 'Centered price'),

    # Whole price only
    ('.a-price-whole', 'Whole dollar amount'),

    # Buy box
    ('#buybox .a-price .a-offscreen', 'Buy box price'),
]

print("FOUND PRICES:")
print("="*70)

all_found = {}

for selector, description in selectors_to_test:
    elements = soup.select(selector)
    if elements:
        prices = []
        for elem in elements[:5]:  # Show first 5
            text = elem.get_text(strip=True)
            prices.append(text)

        if prices:
            all_found[selector] = prices
            print(f"\n✓ {description}")
            print(f"  Selector: {selector}")
            print(f"  Found {len(elements)} price(s):")
            for i, price in enumerate(prices, 1):
                print(f"    {i}. {price}")

print("\n" + "="*70)
print("RECOMMENDATION:")
print("="*70)

# Find which selector contains 264.99
target_price = "264.99"
found_selector = None

for selector, prices in all_found.items():
    for price in prices:
        if target_price in price:
            found_selector = selector
            print(f"\n✓ Found ${target_price} using selector:")
            print(f"  \"{selector}\"")
            break
    if found_selector:
        break

if not found_selector:
    print("\nThe target price $264.99 was not found in this fetch.")
    print("This could mean:")
    print("1. Amazon is showing different prices based on your location/session")
    print("2. The price has changed")
    print("3. You need to select a specific seller")
    print("\nMost reliable selector for Amazon main price:")
    print("  \".a-price .a-offscreen\"")
    print("\nThis will get the FIRST price on the page (usually the main offer)")

print("\n" + "="*70)
print("TO USE IN YOUR CONFIG:")
print("="*70)
print('''
{
  "name": "JONSBO N5 NAS Pc Case",
  "url": "https://www.amazon.com/JONSBO-Supports-Built-Veneer-Computer/dp/B0DG2N3PBB",
  "parameter": "price",
  "css_selector": ".a-price .a-offscreen",
  "threshold": 260,
  "currency": "USD",
  "enabled": true
}
''')

print("\nNOTE: If the first price isn't the one you want, try:")
print("  - Use different selector from the list above")
print("  - Or modify the scraper to select a specific index")
