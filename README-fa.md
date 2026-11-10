# billiger-mcp 🛒

mcp-name: io.github.mohammad-abbasi-sh/billiger-mcp

سرور MCP غیررسمی و **فقط‌خواندنی** برای **[billiger.de](https://www.billiger.de)** — مقایسهٔ قیمت آلمان از billiger.de (رایگان، بدون کلید): جست‌وجوی محصولات با بهترین قیمت، مقایسهٔ پیشنهادهای فروشگاه‌ها و تخفیف‌های روز. بدون کلید، بدون ورود.

> ساختهٔ محمد عباسی، بخشی از «کارخانهٔ MCP آلمان». وابسته به billiger.de نیست.

## برای ایجنت‌های هوش مصنوعی

به پیکربندی MCP کلاینت اضافه کنید (stdio):

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

یا به‌صورت محلی اجرا کنید: `python -m billiger_mcp.server` (نیازمند `mcp<2` و `httpx`).

## ابزارها

| ابزار | توضیح |
|------|-------|
| `billiger_search_prices` | جست‌وجوی محصولات با بهترین قیمت |
| `billiger_product_offers` | مقایسهٔ پیشنهادهای فروشگاه‌ها برای یک محصول |
| `billiger_best_deals` | تخفیف‌های روز از صفحهٔ اصلی |
| `billiger_health` | بررسی دسترس‌پذیری (ok / blocked / error) — یک درخواست مؤدبانه |

## توسعه

```bash
python3 -m venv .venv && .venv/bin/pip install "mcp<2" httpx pytest
.venv/bin/pip install -e .
.venv/bin/python -m pytest tests/ -q
```

## لایسنس

MIT

---

Built by [Mohammad Abbasi](https://github.com/mohammad-abbasi-sh) — [Almanibama](https://almanibama.ir) · [mabbasi.ir](https://mabbasi.ir)
