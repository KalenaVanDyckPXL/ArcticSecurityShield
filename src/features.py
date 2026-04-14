"""
features.py - URL feature extraction
Extracts 15 features from a URL string for the classifier.
"""

import re
from typing import List

FEATURE_COLS: List[str] = [
    "url_length", "num_dots", "num_hyphens", "num_underscores",
    "num_slashes", "num_at", "num_question", "num_equals",
    "num_digits", "has_suspicious_word", "has_ip", "has_https",
    "is_shortened", "domain_length", "subdomain_count",
]

# Words that appear often in phishing URLs but rarely in legitimate ones
SUSPICIOUS_WORDS = [
    "login", "verify", "update", "secure", "account", "bank",
    "paypal", "ebay", "confirm", "password", "free", "winner",
    "claim", "urgent", "alert", "signin", "credential", "suspend",
]

SHORTENER_DOMAINS = [
    "bit.ly", "tinyurl.com", "goo.gl", "ow.ly", "t.co",
    "rebrand.ly", "is.gd", "buff.ly", "short.io",
]

IP_PATTERN = re.compile(r'https?://\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}')


def extract_features(url: str) -> dict:
    u = str(url).strip().lower()

    try:
        domain_part = u.split("/")[2] if "/" in u else u
        domain_length = len(domain_part)
    except Exception:
        domain_length = 0

    num_dots = u.count(".")

    return {
        "url_length":          len(u),
        "num_dots":            num_dots,
        "num_hyphens":         u.count("-"),
        "num_underscores":     u.count("_"),
        "num_slashes":         u.count("/"),
        "num_at":              u.count("@"),
        "num_question":        u.count("?"),
        "num_equals":          u.count("="),
        "num_digits":          sum(c.isdigit() for c in u),
        "has_suspicious_word": int(any(w in u for w in SUSPICIOUS_WORDS)),
        "has_ip":              int(bool(IP_PATTERN.search(u))),
        "has_https":           int(u.startswith("https")),
        "is_shortened":        int(any(s in u for s in SHORTENER_DOMAINS)),
        "domain_length":       domain_length,
        "subdomain_count":     max(0, num_dots - 1),
    }
