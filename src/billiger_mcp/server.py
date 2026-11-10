"""MCP server: unofficial read-only access to billiger.de, Germany's
price-comparison portal (~3.2M visits/month). No key, no login —
but the site sits behind Cloudflare: the full browser navigation
header set in http.py is required (a bare UA gets the 403
"Just a moment..." challenge). Search resolves to a category page
or /noresult; product pages list the first 20 offers server-side
(the page total is reported). NOTE: no price-history tool — the
chart is JS-loaded with no data in the HTML."""
from __future__ import annotations

import json
import sys
from datetime import datetime, timezone

from mcp.server.fastmcp import FastMCP

from . import domain as _dom
from . import http as _http

INSTRUCTIONS = """\
Unofficial read-only MCP server for billiger.de price comparison \
(no key, no login): search products with best prices, compare shop \
offers for one product (price, shipping, total, delivery), and \
today's deals from the home page. NOTE: no price-history tool — the \
price chart is JS-loaded and its data is not in the HTML. Prices \
are "from" prices (ab) in EUR; offers are the first 20 server-side \
rows, the page total is reported. Built by Mohammad Abbasi \
(mohammad-abbasi-sh) — https://almanibama.ir · https://mabbasi.ir \
— Germany MCP factory.\
"""

_SOURCE = "billiger.de"
_DISCLAIMER = ("Unofficial read-only data from billiger.de; verify on "
               "the site before acting on it.")


def _envelope() -> dict:
    return {
        "fetched_at": datetime.now(timezone.utc).isoformat(),
        "source": _SOURCE,
        "disclaimer": _DISCLAIMER,
    }


def _ok(payload: dict) -> str:
    return json.dumps({**_envelope(), **payload}, ensure_ascii=False)


def _err(e: Exception) -> str:
    return _ok({"error": str(e)})


mcp = FastMCP("billiger-mcp", instructions=INSTRUCTIONS)


@mcp.tool()
def billiger_search_prices(query: str, limit: int = 10) -> str:
    """Search billiger.de products by name: best ("ab") price in
    EUR, number of offers, rating and review count. query: e.g.
    iphone, samsung fernseher, waschmaschine. limit: 1..20
    (default 10)."""
    try:
        q = _dom.validate_query(query)
        lim = _dom.validate_limit(limit)
        items = _dom.parse_cards(
            _http.fetch_text(_dom.search_url(q)))
    except (_http.BilligerMcpError, ValueError) as e:
        return _err(e)
    return _ok({"query": q, "total_results": len(items),
                "count": min(lim, len(items)), "items": items[:lim]})


@mcp.tool()
def billiger_product_offers(product: str, limit: int = 10) -> str:
    """Compare shop offers for one product: shop, seller, variant,
    price, shipping, total and delivery time. product: a billiger.de
    /baseproducts/ URL, a slug (114326-apple-iphone-17) or a numeric
    id (114326). limit: 1..20 (default 10). Only the first 20
    offers are on the page; total_offers reports the page total."""
    try:
        lim = _dom.validate_limit(limit)
        url = _dom.resolve_product_url(product)
        out = _dom.parse_offers(_http.fetch_text(url))
    except (_http.BilligerMcpError, ValueError) as e:
        return _err(e)
    offers = out["offers"]
    return _ok({"product": product, "url": url,
                "product_name": out["product_name"],
                "total_offers": out["total_offers"],
                "shown_offers": min(lim, len(offers)),
                "count": min(lim, len(offers)),
                "items": offers[:lim]})


@mcp.tool()
def billiger_best_deals(limit: int = 10) -> str:
    """Today's deals from the billiger.de home page: product, best
    ("ab") price in EUR and number of offers. limit: 1..20
    (default 10)."""
    try:
        lim = _dom.validate_limit(limit)
        items = _dom.parse_cards(
            _http.fetch_text("https://www.billiger.de/"))
    except (_http.BilligerMcpError, ValueError) as e:
        return _err(e)
    return _ok({"total_results": len(items),
                "count": min(lim, len(items)), "items": items[:lim]})


@mcp.tool()
def billiger_health() -> str:
    """Check whether billiger.de is reachable right now.

    Returns status ok (HTTP 200), blocked (HTTP 403/429 — bot wall or
    rate limit) or error, plus the HTTP status and the probed URL.
    One polite request; it does not fetch any listings."""
    return _ok(_http.health_check())


def main() -> None:
    mcp.run()


if __name__ == "__main__":
    sys.exit(main())
