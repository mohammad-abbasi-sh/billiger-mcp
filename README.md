# billiger-mcp 🛒

> ⚠️ **Status: DEGRADED (2026-11-12)** — billiger.de currently blocks automated access (HTTP 403) from this environment. All tools return a clear "blocked" error until the site allows access again. Check `billiger_health` for the live status.


mcp-name: io.github.mohammad-abbasi-sh/billiger-mcp

Unofficial **read-only** MCP server for **[billiger.de](https://www.billiger.de)** — German price comparison from billiger.de (free, no key, no login): search products with best prices, compare shop offers, and today's deals. No key, no login.

> Built by Mohammad Abbasi as part of the "Germany MCP factory". Not affiliated with billiger.de.

## For AI agents

Add to your MCP client config (stdio):

```json
{
  "mcpServers": {
    "billiger": {
      "command": "uvx",
      "args": ["billiger-mcp==0.1.0"]
    }
  }
}
```

Or run locally: `python -m billiger_mcp.server` (needs `mcp<2`, `httpx`).

## Tools

| Tool | Description |
|------|-------------|
| `billiger_search_prices` | Search billiger.de products by name: best price, offer count, rating — `query`, `limit` 1..20 |
| `billiger_product_offers` | Compare shop offers for one product (shop, price, shipping, total, delivery) — `product` (billiger.de URL, baseproducts id or slug), `limit` 1..20 |
| `billiger_best_deals` | Today's deals from the billiger.de home page: product, best price, offer count — `limit` 1..20 |
| `billiger_health` | Reachability probe (ok / blocked / error) — one polite request |

## Development

```bash
python3 -m venv .venv && .venv/bin/pip install "mcp<2" httpx pytest
.venv/bin/pip install -e .
.venv/bin/python -m pytest tests/ -q
```

## License

MIT

---

Built by [Mohammad Abbasi](https://github.com/mohammad-abbasi-sh) — [Almanibama](https://almanibama.ir) · [mabbasi.ir](https://mabbasi.ir)
