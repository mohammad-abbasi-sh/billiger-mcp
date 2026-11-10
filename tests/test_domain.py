"""Offline tests — parse real captured billiger.de pages
(scripts/styles stripped), no network."""
import json
import pathlib
import sys
import unittest
from unittest import mock

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent / "src"))

from billiger_mcp import domain as dom
from billiger_mcp import server as srv

FIX = pathlib.Path(__file__).resolve().parent / "fixtures"


def _read(name):
    return (FIX / name).read_text(encoding="utf-8")


class TestValidation(unittest.TestCase):
    def test_query_and_limit(self):
        self.assertEqual(dom.validate_query("  iphone "), "iphone")
        with self.assertRaises(ValueError):
            dom.validate_query("")
        self.assertEqual(dom.validate_limit(10), 10)
        with self.assertRaises(ValueError):
            dom.validate_limit(21)

    def test_price(self):
        self.assertEqual(dom.parse_de_price("839,99"), 839.99)
        self.assertEqual(dom.parse_de_price("2.999,00"), 2999.0)

    def test_resolve_product_url(self):
        self.assertEqual(
            dom.resolve_product_url("114326"),
            "https://www.billiger.de/baseproducts/114326")
        self.assertEqual(
            dom.resolve_product_url("114326-apple-iphone-17"),
            "https://www.billiger.de/baseproducts/114326-apple-iphone-17")
        self.assertEqual(
            dom.resolve_product_url(
                "https://www.billiger.de/baseproducts/114326-apple-iphone-17"),
            "https://www.billiger.de/baseproducts/114326-apple-iphone-17")
        with self.assertRaises(ValueError):
            dom.resolve_product_url("https://example.com/x")
        with self.assertRaises(ValueError):
            dom.resolve_product_url("not a product")


class TestSearchIphone(unittest.TestCase):
    def setUp(self):
        self.items = dom.parse_cards(_read("search-iphone.html"))

    def test_count(self):
        self.assertEqual(len(self.items), 21)

    def test_first_card(self):
        self.assertEqual(self.items[0], {
            "id": "114326", "name": "Apple iPhone 17",
            "url": "https://www.billiger.de/baseproducts/114326-apple-iphone-17",
            "price_from_eur": 839.99, "offers": 418,
            "rating_pct": 92, "reviews": 173})

    def test_second_card(self):
        self.assertEqual(self.items[1]["name"], "Apple iPhone 17 Pro")
        self.assertEqual(self.items[1]["price_from_eur"], 1089.0)
        self.assertEqual(self.items[1]["offers"], 291)

    def test_all_have_price_and_url(self):
        for c in self.items:
            self.assertIsInstance(c["price_from_eur"], float)
            self.assertTrue(c["url"].startswith(
                "https://www.billiger.de/baseproducts/"))

    def test_nomatch(self):
        self.assertEqual(dom.parse_cards(_read("search-nomatch.html")),
                         [])


class TestHome(unittest.TestCase):
    def test_home_cards(self):
        items = dom.parse_cards(_read("home.html"))
        self.assertEqual(len(items), 37)
        self.assertEqual(items[0]["name"], "Apple iPhone 17")
        self.assertEqual(items[0]["price_from_eur"], 839.99)
        self.assertEqual(items[1]["name"], "Sony PlayStation 5")
        self.assertEqual(items[1]["price_from_eur"], 599.99)


class TestProductOffers(unittest.TestCase):
    def setUp(self):
        self.out = dom.parse_offers(_read("product-iphone17.html"))

    def test_meta(self):
        self.assertEqual(self.out["product_name"], "Apple iPhone 17")
        self.assertEqual(self.out["total_offers"], 385)
        self.assertEqual(len(self.out["offers"]), 20)

    def test_first_offer(self):
        self.assertEqual(self.out["offers"][0], {
            "shop": "ebay.de", "seller": "ms-electronics*net",
            "variant": "256 GB Nebelblau", "price_eur": 839.99,
            "was_price_eur": None,
            "shipping_eur": 0.0, "total_eur": 839.99,
            "delivery": "1-5 Werktage", "shop_rating_pct": 100})

    def test_sale_offer(self):
        # Joybuy row: sale price via data-sales-price + struck-through
        # old price.
        sale = [o for o in self.out["offers"]
                if o["shop"] == "Joybuy"][0]
        self.assertEqual(sale["price_eur"], 919.0)
        self.assertEqual(sale["was_price_eur"], 1099.0)

    def test_all_have_shop_and_price(self):
        for o in self.out["offers"]:
            self.assertIsInstance(o["shop"], str)
            self.assertIsInstance(o["price_eur"], float)
            self.assertIsInstance(o["total_eur"], float)


class TestServerWiring(unittest.TestCase):
    def _fetch(self, url):
        if "searchstring=iphone" in url:
            return _read("search-iphone.html")
        if "baseproducts/114326" in url:
            return _read("product-iphone17.html")
        if url == "https://www.billiger.de/":
            return _read("home.html")
        raise AssertionError(f"unexpected URL: {url}")

    def test_search_uses_fixture(self):
        with mock.patch("billiger_mcp.server._http.fetch_text",
                        side_effect=self._fetch):
            out = json.loads(srv.billiger_search_prices("iphone", limit=3))
        self.assertNotIn("error", out)
        self.assertEqual(out["source"], "billiger.de")
        self.assertEqual(out["total_results"], 21)
        self.assertEqual(out["count"], 3)
        self.assertEqual(out["items"][0]["name"], "Apple iPhone 17")

    def test_offers_uses_fixture(self):
        with mock.patch("billiger_mcp.server._http.fetch_text",
                        side_effect=self._fetch):
            out = json.loads(srv.billiger_product_offers("114326"))
        self.assertNotIn("error", out)
        self.assertEqual(out["product_name"], "Apple iPhone 17")
        self.assertEqual(out["total_offers"], 385)
        self.assertEqual(out["count"], 10)
        self.assertEqual(out["items"][0]["shop"], "ebay.de")

    def test_deals_uses_fixture(self):
        with mock.patch("billiger_mcp.server._http.fetch_text",
                        side_effect=self._fetch):
            out = json.loads(srv.billiger_best_deals(limit=5))
        self.assertNotIn("error", out)
        self.assertEqual(out["total_results"], 37)
        self.assertEqual(out["items"][1]["name"], "Sony PlayStation 5")

    def test_invalid_product(self):
        out = json.loads(srv.billiger_product_offers("not a product"))
        self.assertIn("error", out)


if __name__ == "__main__":
    unittest.main()
