# ArcticSecurityShield - System Architecture

## Overview

ArcticSecurityShield uses a hybrid approach: supervised ML for generalisation
across unseen examples, combined with rule-based layers for specific attack
patterns that are hard to learn from data alone.

```
User Input
    |
    +---> URL ──────────────────────────────────────────────+
    |         feature extraction (15 features)              |
    |         Random Forest classifier                       |
    |         + Typosquatting layer (Levenshtein)           |
    |                                                        |
    +---> Email ────────────────────────────────────────────+
    |         TF-IDF vectorisation (15k features)           |
    |         Logistic Regression classifier                 |
    |         + Rule-based scorer (urgency, 419, hidden      |
    |           hyperlinks, anchor text)                     |
    |         + Probability floor (advance fee fraud)       |
    |                                                        +---> Risk score
    +---> Phone ────────────────────────────────────────────+      (Low / Medium / High)
              feature extraction (16 features)              |         |
              Random Forest classifier                       |         v
              + Rule-based flags (premium, scam CC)         |    Plain-language
                                                            |    explanation
                                                            |    (hardcoded or LLM)
                                                            |         |
                                                            |         v
                                                            |    Flask web UI
                                                            |    + Gmail add-on
```

## URL classifier

**Features (15):** url_length, num_dots, num_hyphens, num_underscores,
num_slashes, num_at, num_question, num_equals, num_digits,
has_suspicious_word, has_ip, has_https, is_shortened, domain_length,
subdomain_count

**Typosquatting layer:**
- Extracts second-level domain from URL
- Normalises homoglyphs: rn→m, 0→o, 1→l, vv→w, etc.
- Computes Levenshtein edit distance to 50+ known brands
- Threshold: distance ≤ 1 for short brands (≤6 chars), ≤ 2 for longer

**Probability blending:**
- If typosquat detected AND ML score < 0.75: score boosted to 0.78

## Email classifier

**Vectorisation:** TF-IDF, unigrams + bigrams, 15,000 features,
sublinear TF scaling

**Rule signals:** urgency phrases (11 patterns), credential requests (4),
prize/lottery (6), money transfer (4), advance fee fraud (18),
suspicious sender, HTML hidden links, anchor text mismatch

**Blending:** 70% ML + 30% rule score. If advance fee detected or
rule score ≥ 7: probability floored at 0.75.

## Phone classifier

**Features (16):** num_digits, too_short, too_long, normal_len, has_plus,
starts_intl, is_premium, is_scam_cc, repeating_digits, sequential_digits,
all_same, starts_0900, starts_090, has_letters, double_cc,
is_nigerian_pattern

**Premium prefixes:** BE 090x, NL 090x-098x, UK 09x, DE 0900/0180,
FR 089x, US 900x

**Scam country codes:** Caribbean callback (+1473, +1268, +1876, +1284,
+1649, +1664, +1758, +1784, +1809, +1829, +1849), Nigeria (+234),
Tanzania (+255), Turkey premium (90850)

## Gmail add-on

```
Gmail (browser)
    |
    v
Google Apps Script (Code.gs)
    |  POST /predict/email
    v
ngrok tunnel (public HTTPS URL)
    |
    v
Flask app (localhost:5000)
    |
    v
email_analyzer.py
    |
    v
JSON response → Apps Script → Gmail UI panel
```

## Training data

| Model | Dataset | Size |
|-------|---------|------|
| URL | sample_urls.csv (curated) | 104 labelled URLs |
| Email | SpamAssassin corpus + synthetic templates | ~1000 emails |
| Phone | Synthetic (documented fraud patterns) | 3000 numbers |
