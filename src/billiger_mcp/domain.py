"""Domain logic: shape billiger.de's server-rendered HTML into
compact dicts (stdlib only, regex parsers).

Data source: https://www.billiger.de — free, no key, no login.
The site sits behind Cloudflare: a bare UA + Accept gets the 403
"Just a moment..." challenge page; the full browser navigation
header set in http.py (sec-ch-ua / sec-fetch, verified 2026-11-10)
lets the real HTML through.

Pages (verified 2026-11-10):
- GET /search?searchstring=<q> — 302s to the matching category
  page (e.g. /categories/4373/53176-apple-handys-ohne-vertrag) or
  to /noresult?searchstring=<q> when nothing matches.
- Product cards (search + home share the structure):
  <a href="/baseproducts/<id>-<slug>" title="<name>"> …
  <span class="line-clamp-2…"> <name> </span> …
  <div … data-bde-price=""> <strong … data-price> <span>ab</span>
  839,99 €* </strong> </div> … <div> 418 Preise vergleichen </div>
  rating: <div … style="--rating: 92"></div> <span>(173)</span>
- GET /baseproducts/<id>-<slug> — product page; offer rows are
  <div … data-product-id="<offer-id>" data-bde-card=""> …
  variant <div … title="<variant>">, shop <img alt="Shop <shop>">,
  seller "Verkäufer: <name>" + --rating, price <span data-price>
  877,89 €*, "ab 0,00 € Versand", "877,89 € Gesamt",
  "Lieferzeit: 1-5 Werktage". First 20 offers are SSR; the page
  total (e.g. 385) is in the meta description.
- GET / (home) — deals: same product-card structure; 37
  /baseproducts/ links on 2026-11-10.
- Price history: NOT in the SSR HTML — the chart is a JS
  component (data-pricehistory-container, empty server-side) with
  no data endpoint in the page. No price_history tool: the data
  is not fetchable read-only from the HTML.
"""
from __future__ import annotations

import html as _html
import re
from urllib.parse import quote_plus

BASE = "https://www.billiger.de"

_CARD_RE = re.compile(
    r'<a[^>]+href="/baseproducts/(\d+)-([^"]+)"[^>]*>',
    re.IGNORECASE)
_NAME_RE = re.compile(
    r'<span class="line-clamp-2[^"]*">\s*([^<]+?)\s*</span>')
_PRICE_RE = re.compile(
    r'data-(?:sales-)?price[^>]*>(?:\s*<span[^>]*>ab</span>)?\s*([\d.]+,\d{2})\s*€')
_WAS_PRICE_RE = re.compile(
    r'line-through">([\d.]+,\d{2})\s*€</span>')
_OFFERS_RE = re.compile(r'(\d[\d.]*)\s+Preise vergleichen')
_RATING_RE = re.compile(r'--rating:\s*(\d+)')
_REVIEWS_RE = re.compile(r'\((\d+)\)')

_OFFER_RE = re.compile(r'data-product-id="(\d+)"')
_VARIANT_RE = re.compile(
    r'<div class="order-1[^"]*" title="([^"]+)">')
_SHOP_RE = re.compile(r'<img[^>]+alt="Shop ([^"]+)"')
_SELLER_RE = re.compile(r'Verkäufer:\s*([^"<]+)')
_SHIP_RE = re.compile(r'ab\s+([\d.]+,\d{2})\s*€ Versand')
_TOTAL_RE = re.compile(r'([\d.]+,\d{2})\s*€ Gesamt')
_DELIVERY_RE = re.compile(r'Lieferzeit:\s*([^<]+)')


def validate_query(query: str) -> str:
    q = (query or "").strip()
    if not q:
        raise ValueError("query must not be empty")
    if len(q) > 100:
        raise ValueError("query too long (max 100 characters)")
    return q


def validate_limit(limit: int, maximum: int = 20) -> int:
    if not 1 <= limit <= maximum:
        raise ValueError(
            f"limit out of range: {limit} (expected 1..{maximum})")
    return limit


def search_url(query: str) -> str:
    return f"{BASE}/search?searchstring={quote_plus(query)}"


def resolve_product_url(product: str) -> str:
    """Full billiger.de URL, a baseproducts slug, or a bare numeric
    id (the site 301s /baseproducts/<id> to the canonical slug
    URL)."""
    p = (product or "").strip()
    if not p:
        raise ValueError("product must not be empty")
    if p.startswith("http"):
        if "billiger.de/baseproducts/" not in p:
            raise ValueError(
                "product URL must be a billiger.de /baseproducts/ URL")
        return p
    if p.startswith("/baseproducts/"):
        return BASE + p
    m = re.match(r"^(\d+)(?:-([A-Za-z0-9-]+))?$", p)
    if not m:
        raise ValueError(
            "product must be a billiger.de URL, a baseproducts slug "
            "(e.g. 114326-apple-iphone-17) or a numeric id")
    if m.group(2):
        return f"{BASE}/baseproducts/{m.group(1)}-{m.group(2)}"
    return f"{BASE}/baseproducts/{m.group(1)}"


def parse_de_price(text: str) -> float:
    """German price string ("2.999,00") -> float."""
    return float(text.replace(".", "").replace(",", "."))


def parse_cards(page_html: str) -> list[dict]:
    """Product cards from a search/category/home page, deduped by
    product id, in page order. [] when the page has no products
    (e.g. the /noresult page)."""
    out: list[dict] = []
    seen: set[str] = set()
    for m in _CARD_RE.finditer(page_html):
        pid, slug = m.group(1), m.group(2)
        if pid in seen:
            continue
        seen.add(pid)
        chunk = page_html[m.start():m.start() + 2500]
        name_m = _NAME_RE.search(chunk)
        price_m = _PRICE_RE.search(chunk)
        offers_m = _OFFERS_RE.search(chunk)
        rating_m = _RATING_RE.search(chunk)
        reviews_m = _REVIEWS_RE.search(chunk)
        name = _html.unescape(
            name_m.group(1).strip()) if name_m else None
        # fallback: the link's title attribute
        if not name:
            t = re.search(r'title="([^"]+)"', m.group(0))
            name = _html.unescape(t.group(1)) if t else slug
        out.append({
            "id": pid,
            "name": name,
            "url": f"{BASE}/baseproducts/{pid}-{slug}",
            "price_from_eur": (parse_de_price(price_m.group(1))
                               if price_m else None),
            "offers": (int(offers_m.group(1).replace(".", ""))
                       if offers_m else None),
            "rating_pct": int(rating_m.group(1)) if rating_m else None,
            "reviews": int(reviews_m.group(1)) if reviews_m else None,
        })
    return out


def parse_offers(page_html: str) -> dict:
    """{product_name, price_from_eur, total_offers, offers: [{shop,
    seller, variant, price_eur, shipping_eur, total_eur,
    delivery, shop_rating_pct}]} — first 20 offers are SSR."""
    name_m = re.search(
        r'<meta property="og:title" content="([^"]+?)(?:💥|$)', page_html)
    total_m = re.search(r'–\s*([\d.]+)\s+Angebote', page_html)
    offers: list[dict] = []
    for m in _OFFER_RE.finditer(page_html):
        chunk = page_html[m.start():m.start() + 4500]
        variant_m = _VARIANT_RE.search(chunk)
        shop_m = _SHOP_RE.search(chunk)
        seller_m = _SELLER_RE.search(chunk)
        price_m = _PRICE_RE.search(chunk)
        was_m = _WAS_PRICE_RE.search(chunk)
        ship_m = _SHIP_RE.search(chunk)
        total_m2 = _TOTAL_RE.search(chunk)
        deliv_m = _DELIVERY_RE.search(chunk)
        rating_m = _RATING_RE.search(chunk)
        if not shop_m and not price_m:
            continue
        offers.append({
            "shop": shop_m.group(1) if shop_m else None,
            "seller": (seller_m.group(1).strip()
                       if seller_m else None),
            "variant": (variant_m.group(1).strip()
                        if variant_m else None),
            "price_eur": (parse_de_price(price_m.group(1))
                          if price_m else None),
            "was_price_eur": (parse_de_price(was_m.group(1))
                              if was_m else None),
            "shipping_eur": (parse_de_price(ship_m.group(1))
                             if ship_m else None),
            "total_eur": (parse_de_price(total_m2.group(1))
                          if total_m2 else None),
            "delivery": (deliv_m.group(1).strip()
                         if deliv_m else None),
            "shop_rating_pct": (int(rating_m.group(1))
                                if rating_m else None),
        })
    return {
        "product_name": (_html.unescape(name_m.group(1).strip())
                         if name_m else None),
        "total_offers": (int(total_m.group(1).replace(".", ""))
                         if total_m else len(offers)),
        "offers": offers,
    }
