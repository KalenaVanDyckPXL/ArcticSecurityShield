"""
translations.py - Dutch/English explanation strings

Detects whether the input is likely Dutch and returns
the appropriate explanation and flag labels.

No external dependencies needed - pure rule-based language detection.
"""

import re

# Dutch word list for detection - common words that don't appear in English
DUTCH_WORDS = [
    # Core Dutch function words (rare or absent in English)
    "de", "het", "een", "van", "zijn", "met", "voor", "aan", "maar",
    "ook", "wel", "niet", "naar", "bij", "als", "uit", "over",
    "door", "heeft", "hebben", "wordt", "worden",
    "mijn", "uw", "ons", "onze", "jullie",
    # Dutch-specific vocabulary
    "wachtwoord", "betaling", "rekening", "bankrekening",
    "betalen", "belasting", "overheid", "inloggen", "bevestigen",
    "geachte", "bedankt", "groeten", "beveiligen", "geblokkeerd",
    "verdacht", "oplichting", "nep", "valse", "beveiliging",
    "klant", "gebruiker", "toegang", "gegevens", "persoonsgegevens",
]

def detect_language(text: str) -> str:
    """Returns 'nl' if Dutch is detected, 'en' otherwise."""
    words = re.findall(r'\b\w+\b', text.lower())
    if not words:
        return "en"
    dutch_hits = sum(1 for w in words if w in DUTCH_WORDS)
    ratio = dutch_hits / len(words)
    return "nl" if ratio > 0.06 else "en"


# ── URL explanations ──────────────────────────────────────────────────────────

URL_EXPLANATIONS = {
    "high": {
        "en": "This link looks very suspicious and has several signs of a phishing attack. Do not click it, and do not enter any personal details.",
        "nl": "Deze link ziet er zeer verdacht uit en vertoont meerdere kenmerken van een phishing-aanval. Klik er niet op en vul geen persoonlijke gegevens in.",
    },
    "medium": {
        "en": "This link has some unusual characteristics. Be careful before clicking. If someone sent you this out of nowhere, it may be a scam.",
        "nl": "Deze link heeft enkele ongewone kenmerken. Wees voorzichtig voor je klikt. Als iemand je dit onverwacht stuurde, kan het een oplichting zijn.",
    },
    "low": {
        "en": "This link appears to be safe. No obvious phishing signals found. Still, always be careful online.",
        "nl": "Deze link lijkt veilig. Geen duidelijke phishing-signalen gevonden. Blijf toch altijd voorzichtig online.",
    },
}

URL_RISK_LABELS = {
    "high":   {"en": "High Risk",    "nl": "Hoog Risico"},
    "medium": {"en": "Medium Risk",  "nl": "Gemiddeld Risico"},
    "low":    {"en": "Low Risk",     "nl": "Laag Risico"},
}


# ── Email explanations ────────────────────────────────────────────────────────

EMAIL_EXPLANATIONS = {
    "high": {
        "en": "This email has multiple strong signs of phishing. Do not click any links. Do not reply with personal info. Report it to your email provider.",
        "nl": "Dit e-mailbericht vertoont meerdere sterke kenmerken van phishing. Klik geen links aan. Antwoord niet met persoonlijke informatie. Meld het bij uw e-mailprovider.",
    },
    "medium": {
        "en": "This email has some suspicious characteristics. Be careful before clicking links. If in doubt, contact the sender via a known number.",
        "nl": "Dit e-mailbericht heeft enkele verdachte kenmerken. Wees voorzichtig met het klikken op links. Neem bij twijfel contact op met de afzender via een bekend nummer.",
    },
    "low": {
        "en": "No strong phishing signals found. Still, always be careful with unexpected emails asking you to act.",
        "nl": "Geen sterke phishing-signalen gevonden. Wees toch altijd voorzichtig met onverwachte e-mails die vragen om actie te ondernemen.",
    },
}


# ── Phone explanations ────────────────────────────────────────────────────────

PHONE_EXPLANATIONS = {
    "high": {
        "en": "This phone number has strong signs of fraud. Do not call it. Do not share any personal or financial information. If you got a call from this number, hang up.",
        "nl": "Dit telefoonnummer vertoont sterke tekenen van fraude. Bel dit nummer niet terug. Deel geen persoonlijke of financiële informatie. Als u gebeld werd door dit nummer, hang dan meteen op.",
    },
    "medium": {
        "en": "This number has some suspicious characteristics. If someone asks you to call it, look up the organisation's official number and use that instead.",
        "nl": "Dit nummer heeft enkele verdachte kenmerken. Als iemand u vraagt dit nummer te bellen, zoek dan het officiële nummer van de organisatie op en gebruik dat.",
    },
    "low": {
        "en": "No obvious fraud signals found for this number. Still, never share personal or financial information with unsolicited callers.",
        "nl": "Geen duidelijke fraudesignalen gevonden voor dit nummer. Deel nooit persoonlijke of financiële informatie met onbekende bellers.",
    },
}


# ── Flag category translations ────────────────────────────────────────────────

FLAG_TRANSLATIONS = {
    "Typosquatting: looks like":                {"nl": "Domeinvervalsing: lijkt op"},
    "edit distance":                            {"nl": "editeerafstand"},
    "Contains suspicious keywords":             {"nl": "Bevat verdachte trefwoorden"},
    "Uses an IP address instead of a domain":   {"nl": "Gebruikt een IP-adres in plaats van een domeinnaam"},
    "URL shortener used":                       {"nl": "URL-verkorter gebruikt — echte bestemming is verborgen"},
    "No HTTPS":                                 {"nl": "Geen HTTPS — verbinding is niet versleuteld"},
    "Contains '@'":                             {"nl": "Bevat '@' — vaak gebruikt om de echte URL te verbergen"},
    "Unusually long URL":                       {"nl": "Ongewoon lange URL"},
    "Many subdomains":                          {"nl": "Veel subdomeinen — veelgebruikte truc"},
    "Urgency / Pressure":                       {"nl": "Urgentie / Druk"},
    "Requests Personal Information":            {"nl": "Vraagt om persoonlijke informatie"},
    "Prize / Lottery Claim":                    {"nl": "Prijs / Loterij claim"},
    "Money Transfer Request":                   {"nl": "Verzoek om geldoverdracht"},
    "Advance Fee Fraud (419 Scam)":             {"nl": "Voorschotfraude (419-oplichting)"},
    "Large Sum of Money Mentioned":             {"nl": "Groot geldbedrag vermeld"},
    "Reply-to Different Address":               {"nl": "Antwoordadres verschilt van afzender"},
    "Suspicious Sender Address":                {"nl": "Verdacht afzenderadres"},
    "Sender Domain Impersonation":              {"nl": "Domeinnaam van afzender vervalst"},
    "Excessive Exclamation Marks":              {"nl": "Overmatig gebruik van uitroeptekens"},
    "Excessive Capital Letters":                {"nl": "Overmatig gebruik van hoofdletters"},
    "Hidden URL Mismatch":                      {"nl": "Verborgen URL-mismatch"},
    "Suspicious Link Behind Text":              {"nl": "Verdachte link achter tekst verborgen"},
    "Possible Hidden Hyperlink":                {"nl": "Mogelijke verborgen hyperlink"},
    "Premium Rate Number":                      {"nl": "Betalend nummer (premium rate)"},
    "Known Scam Country Code":                  {"nl": "Bekend frauduleus landnummer"},
    "Suspicious Number Pattern":                {"nl": "Verdacht nummerpatroon"},
    "Premium Prefix (090x)":                    {"nl": "Premium prefix (090x)"},
    "Possible Caller ID Spoofing":              {"nl": "Mogelijke nummeridentiteitsfraude"},
    "Unusual Number Length":                    {"nl": "Ongewone nummerlengte"},
}


def translate_flag(flag: dict, lang: str) -> dict:
    """Translate a flag dict's category to Dutch if needed."""
    if lang == "en":
        return flag
    if isinstance(flag, str):
        for en, translations in FLAG_TRANSLATIONS.items():
            if en.lower() in flag.lower():
                return flag.replace(en, translations.get("nl", en))
        return flag

    result = dict(flag)
    category = flag.get("category", "")
    for en, translations in FLAG_TRANSLATIONS.items():
        if en.lower() in category.lower():
            result["category"] = category.replace(en, translations.get("nl", en))
            break
    return result


def get_explanation(scan_type: str, risk_level: str, lang: str) -> str:
    tables = {"url": URL_EXPLANATIONS, "email": EMAIL_EXPLANATIONS, "phone": PHONE_EXPLANATIONS}
    table = tables.get(scan_type, URL_EXPLANATIONS)
    return table.get(risk_level, table["low"]).get(lang, table[risk_level]["en"])


def get_risk_label(risk_level: str, lang: str) -> str:
    return URL_RISK_LABELS.get(risk_level, URL_RISK_LABELS["low"]).get(lang, risk_level)
