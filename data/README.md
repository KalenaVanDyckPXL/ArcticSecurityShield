# Data

This folder contains datasets used by ArcticSecurityShield.

## Files in this folder

| File | Committed | Description |
|---|---|---|
| `sample_urls.csv` | Yes | 50 hand-curated URLs (25 benign, 25 phishing) for quick testing |
| `malicious_phish.csv` | No (too large) | Full Kaggle dataset - download manually (see below) |

---

## Downloading the full dataset

### Option 1: Kaggle Malicious URLs (recommended)
1. Go to https://www.kaggle.com/datasets/sid321axn/malicious-urls-dataset
2. Download `malicious_phish.csv`
3. Place it in this `data/` folder

### Option 2: UCI Phishing Websites
- Loaded automatically via `ucimlrepo` - no manual download needed
- Used in `notebooks/01_exploration.ipynb`

### Option 3: PhishTank (most up-to-date)
1. Register at https://phishtank.org/developer_info.php
2. Download the verified phishing URLs CSV
3. Place it in `data/` and update the path in `src/train.py`

---

## Data format

Both `sample_urls.csv` and `malicious_phish.csv` use the same format:

```
url,type
https://www.google.com,benign
http://paypal-login-secure.com/verify,phishing
```

The `type` column can contain: `benign`, `phishing`, `malware`, `defacement`
ShieldSense treats anything that is not `benign` as the positive (phishing) class.

---

## Privacy & Ethics

- `sample_urls.csv` contains only publicly known URLs — no personal data
- No user-submitted URLs are stored anywhere in this project
- Full dataset provenance is documented above for reproducibility
