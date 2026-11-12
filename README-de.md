# billiger-mcp 🛒

> ⚠️ **Status: DEGRADED (2026-11-12)** — billiger.de blockiert derzeit den automatisierten Zugriff (HTTP 403) aus dieser Umgebung. Alle Tools geben einen klaren „blocked“-Fehler zurück, bis die Seite den Zugriff wieder erlaubt. Aktuellen Status mit `billiger_health` prüfen.


mcp-name: io.github.mohammad-abbasi-sh/billiger-mcp

Inoffizieller **nur lesender** MCP-Server für **[billiger.de](https://www.billiger.de)** — Deutscher Preisvergleich von billiger.de (kostenlos, kein Schlüssel, kein Login): Produkte mit Bestpreisen suchen, Shop-Angebote vergleichen und Tagesdeals. Kein Schlüssel, keine Anmeldung.

> Gebaut von Mohammad Abbasi als Teil der "Germany MCP factory". Nicht mit billiger.de verbunden.

## Für KI-Agenten

Zur MCP-Client-Konfiguration hinzufügen (stdio):

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

Oder lokal starten: `python -m billiger_mcp.server` (benötigt `mcp<2`, `httpx`).

## Tools

| Tool | Beschreibung |
|------|-------------|
| `billiger_search_prices` | Produkte mit Bestpreisen suchen |
| `billiger_product_offers` | Shop-Angebote für ein Produkt vergleichen |
| `billiger_best_deals` | Tagesdeals von der Startseite |
| `billiger_health` | Erreichbarkeitsprüfung (ok / blocked / error) — eine höfliche Anfrage |

## Entwicklung

```bash
python3 -m venv .venv && .venv/bin/pip install "mcp<2" httpx pytest
.venv/bin/pip install -e .
.venv/bin/python -m pytest tests/ -q
```

## Lizenz

MIT

---

Built by [Mohammad Abbasi](https://github.com/mohammad-abbasi-sh) — [Almanibama](https://almanibama.ir) · [mabbasi.ir](https://mabbasi.ir)
