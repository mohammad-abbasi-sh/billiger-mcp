"""Live tests — hit the real billiger.de. Cautious: few requests.

Run:  pytest tests/test_live.py -v
Skip: pytest -m "not live"  (or set BILLIGER_SKIP_LIVE=1)
"""
import json
import os
import pathlib
import sys
import unittest

import pytest

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent / "src"))

from billiger_mcp import server as srv

pytestmark = pytest.mark.live
SKIP = os.environ.get("BILLIGER_SKIP_LIVE") == "1"


@pytest.mark.skipif(SKIP, reason="BILLIGER_SKIP_LIVE=1")
class TestLive(unittest.TestCase):
    def test_search_live(self):
        out = json.loads(srv.billiger_search_prices("iphone", limit=3))
        self.assertNotIn("error", out)
        self.assertGreaterEqual(out["total_results"], 5)
        self.assertIn("iPhone", out["items"][0]["name"])
        print(f"\nLIVE search iphone: {out['total_results']} products — "
              f"top: {out['items'][0]['name']} ab "
              f"{out['items'][0]['price_from_eur']} EUR, "
              f"{out['items'][0]['offers']} offers")

    def test_offers_live(self):
        out = json.loads(srv.billiger_product_offers("114326", limit=3))
        self.assertNotIn("error", out)
        self.assertGreaterEqual(out["total_offers"], 50)
        self.assertEqual(len(out["items"]), 3)
        print(f"\nLIVE offers iPhone 17: {out['total_offers']} total — "
              f"cheapest shown: {out['items'][0]['shop']} "
              f"{out['items'][0]['price_eur']} EUR")

    def test_deals_live(self):
        out = json.loads(srv.billiger_best_deals(limit=3))
        self.assertNotIn("error", out)
        self.assertGreaterEqual(out["total_results"], 5)
        print(f"\nLIVE deals: {out['total_results']} products — "
              f"top: {out['items'][0]['name']}")

    def test_nomatch_live(self):
        out = json.loads(srv.billiger_search_prices("xyzqweabc"))
        self.assertNotIn("error", out)
        self.assertEqual(out["total_results"], 0)
