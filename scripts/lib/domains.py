"""Ported 1:1 from scripts/lib/domains.js. The 5 businesses used in every
provider's benchmark run in this project, confirmed identically across all
5 providers' domain-summary.json files (see data/analysis/<api>/domain-summary.json)."""
import time

DOMAINS = [
    "www.thepearlsource.com",
    "www.shein.com",
    "temu.com",
    "www.aliexpress.com",
    "thehalara.com",
]

TARGET_REVIEWS_PER_BUSINESS = 200


def sleep(seconds):
    time.sleep(seconds)
