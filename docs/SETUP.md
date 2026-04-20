# ArcticSecurityShield - Setup Guide

## Requirements

- Python 3.10+
- pip
- Git

## Installation

```bash
git clone https://github.com/KalenaVanDyckPXL/arcticsecurityshield.git
cd arcticsecurityshield
pip install -r requirements.txt
```

## Train models (first time only)

Pre-trained models are included in models/ - skip this if they are present.

```bash
python src/train.py
python src/train_email.py
python src/train_phone.py
```

## Run

```bash
python app/arcticsecurityshield_app.py
# Open: http://localhost:5000
```

## Gmail add-on

See gmail-addon/SETUP.md

## Optional: LLM explanations (for example: Gemini)

```bash
cp .env.example .env
# Edit .env: add GEMINI_API_KEY=your_key
pip install google-genai python-dotenv
python test_llm_debug.py  # verify it works
```
