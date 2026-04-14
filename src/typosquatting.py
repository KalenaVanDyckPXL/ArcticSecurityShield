"""
typosquatting.py - Brand impersonation detection
Checks if a domain is trying to impersonate a known brand
using Levenshtein edit distance and homoglyph substitution.
"""

import re
from typing import Optional

KNOWN_BRANDS = [
    "google", "microsoft", "apple", "amazon", "facebook", "instagram",
    "twitter", "linkedin", "youtube", "netflix", "spotify", "adobe",
    "dropbox", "github", "stackoverflow", "wikipedia",
    "paypal", "visa", "mastercard", "bankofamerica", "chase", "wellsfargo",
    "hsbc", "barclays", "ing", "rabobank", "abnamro", "bunq",
    "ebay", "aliexpress", "bol", "zalando", "coolblue",
    "belastingdienst", "overheid", "rijksoverheid", "politie",
    "kpn", "vodafone", "ziggo", "telenet",
    "dhl", "fedex", "ups", "postnl", "bpost",
    "gmail", "outlook", "yahoo", "hotmail", "protonmail",
]

# Digit/letter swaps commonly used in phishing domains
_HOMOGLYPHS = {"0": "o", "1": "l", "3": "e", "4": "a", "5": "s", "6": "g", "7": "t", "8": "b", "9": "g"}


def _levenshtein(s1: str, s2: str) -> int:
    if len(s1) < len(s2):
        return _levenshtein(s2, s1)
    if not s2:
        return len(s1)
    prev = list(range(len(s2) + 1))
    for c1 in s1:
        curr = [prev[0] + 1]
        for j, c2 in enumerate(s2):
            curr.append(min(prev[j + 1] + 1, curr[j] + 1, prev[j] + (c1 != c2)))
        prev = curr
    return prev[-1]


def _normalize(domain: str) -> str:
    """Replace common homoglyphs so g00gle -> google, rnicrosoft -> microsoft."""
    d = domain.lower()
    d = d.replace("rn", "m").replace("vv", "w")
    for fake, real in _HOMOGLYPHS.items():
        d = d.replace(fake, real)
    return d


def _sld(url: str) -> str:
    """Extract the second-level domain from a URL."""
    u = re.sub(r'^https?://', '', url.lower().strip())
    u = u.split('/')[0].split(':')[0]
    parts = u.split('.')
    return parts[-2] if len(parts) >= 2 else u


def check_typosquatting(url: str) -> dict:
    raw = _sld(url)
    norm = _normalize(raw)

    best_brand, best_dist, is_via_norm = None, 999, False

    for brand in KNOWN_BRANDS:
        d_raw  = _levenshtein(raw, brand)
        d_norm = _levenshtein(norm, brand)

        # Exact match on the raw domain means it's legitimate
        if d_raw == 0:
            return {"is_typosquat": False, "matched_brand": brand, "distance": 0, "explanation": None}

        if d_norm < best_dist or (d_norm == best_dist and d_raw < 999):
            best_dist = d_norm
            best_brand = brand
            is_via_norm = (d_norm < d_raw)

    threshold = 1 if len(best_brand or "") <= 6 else 2

    if best_dist <= threshold and best_brand:
        method = "homoglyph substitution" if is_via_norm else "character substitution"
        explanation = (
            f"This domain looks very similar to '{best_brand}.com' "
            f"({method}, edit distance {best_dist}). "
            f"Attackers register nearly identical domains to impersonate trusted brands."
        )
        return {
            "is_typosquat": True,
            "matched_brand": best_brand,
            "distance": best_dist,
            "explanation": explanation,
        }

    return {"is_typosquat": False, "matched_brand": None, "distance": best_dist, "explanation": None}
