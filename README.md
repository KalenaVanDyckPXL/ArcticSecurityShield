# ArcticSecurityShield

AI-powered scam and phishing detector for vulnerable groups.
Detects phishing URLs, scam emails, and fraudulent phone numbers.
Explains every result in plain language - no technical knowledge needed.

**GRAILS 2026 | SDG 10 | Arctic Intelligence | PXL Digital**

---

## Quick start

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Train the models (only needed once)
python src/train.py
python src/train_email.py
python src/train_phone.py

# 3. Start the app
python app/arcticsecurityshield_app.py

# 4. Open in browser
# http://localhost:5000
```

---

## Project structure

```
arcticsecurityshield/
├── app/
│   └── arcticsecurityshield_app.py   Flask web app (3 tabs)
├── src/
│   ├── features.py                   URL feature extraction (15 features)
│   ├── predict.py                    URL phishing prediction
│   ├── typosquatting.py              Brand impersonation detection
│   ├── email_analyzer.py             Email phishing analysis
│   ├── phone_checker.py              Phone fraud detection
│   ├── explainer.py                  LLM explanation module (optional)
│   ├── train.py                      Train URL model
│   ├── train_email.py                Train email model
│   └── train_phone.py                Train phone model
├── models/                           Trained model files (.pkl)
├── data/                             Training datasets
├── gmail-addon/                      Gmail add-on (Apps Script)
├── docs/                             Full documentation
│   ├── HANDLEIDING_NL.md             Nederlandse handleiding
│   ├── SETUP.md                      English setup guide
│   ├── ARCHITECTURE.md               System architecture
│   └── GRAILS_QA.md                  Q&A prep for judges
├── .env.example                      API key template (optional LLM)
├── requirements.txt                  Python dependencies
└── README.md                         This file
```

---

## Three models

| Module | Algorithm | What it detects |
|--------|-----------|-----------------|
| URL scanner | Random Forest + typosquatting | Phishing links, brand impersonation |
| Email analyser | TF-IDF + Logistic Regression + rules | Credential harvesting, 419 scams, hidden links |
| Phone checker | Random Forest + rules | Premium rate, callback scams, spoofed numbers |

---

## Optional: LLM explanations

The app works fully without an API key. To enable AI-generated explanations:

1. Get a free key at aistudio.google.com
2. Copy `.env.example` to `.env`
3. Add your key: `API_KEY=your_key_here`
4. install needed for API Key, for example Gemini API: `pip install google-genai python-dotenv`

---

## Optional: Gmail add-on

See `gmail-addon/SETUP.md` for instructions.
Requires ngrok (free) to expose localhost to the internet.

---

## Team

Arctic Intelligence - PXL Digital, Bachelor Systems & Networks 2026

Rongjincheng Xiang (PM) | Kalena Van Dyck (ML) | Stef Van de Pol (Backend) | Quynh Huong Vu (Frontend)
