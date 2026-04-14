"""
train_phone.py - Train the phone fraud classifier

No large public phone scam dataset exists, so we generate a synthetic
dataset based on documented fraud patterns (premium rate prefixes,
callback scam country codes, caller ID spoofing) and train a Random Forest
on extracted numerical features.

Usage:
  python src/train_phone.py
"""

import os
import sys
import re
import random
import warnings

import pandas as pd
import numpy as np
import joblib

warnings.filterwarnings("ignore")
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split, cross_val_score, StratifiedKFold
from sklearn.metrics import classification_report, roc_auc_score, f1_score

MODEL_PATH = "models/phone_model.pkl"
FEATS_PATH = "models/phone_feature_cols.pkl"

PREMIUM_PREFIXES = {
    "be": ["090"],
    "nl": ["090", "091", "092", "093", "094", "095", "096", "097", "098"],
    "uk": ["09"],
    "de": ["0900", "0180"],
    "fr": ["089"],
    "us": ["900"],
}

SCAM_COUNTRY_CODES = [
    "1473", "1268", "1876", "1284", "1649", "1664", "1758", "1784",
    "1809", "1829", "1849",
    "255",   # Tanzania
    "234",   # Nigeria
    "90850", # Turkey premium
]


def extract_phone_features(number: str) -> dict:
    cleaned = re.sub(r'[\s\-\.\(\)\/]', '', str(number).strip())
    digits  = re.sub(r'\D', '', cleaned)

    is_premium = 0
    for _, prefixes in PREMIUM_PREFIXES.items():
        for pfx in prefixes:
            if digits.startswith(pfx) or (len(digits) > 2 and digits[2:].startswith(pfx)):
                is_premium = 1
                break

    stripped_digits = re.sub(r'\D', '', re.sub(r'^(\+|00)', '', cleaned))
    is_scam_cc = 0
    for cc in SCAM_COUNTRY_CODES:
        if stripped_digits.startswith(cc) or digits.startswith(cc):
            is_scam_cc = 1
            break

    num_digits = len(digits)
    return {
        "num_digits":          num_digits,
        "too_short":           int(num_digits < 7),
        "too_long":            int(num_digits > 15),
        "normal_len":          int(7 <= num_digits <= 15),
        "has_plus":            int(cleaned.startswith('+')),
        "starts_intl":         int(cleaned.startswith('+') or cleaned.startswith('00')),
        "is_premium":          is_premium,
        "is_scam_cc":          is_scam_cc,
        "repeating_digits":    int(bool(re.search(r'(\d)\1{4,}', digits))),
        "sequential_digits":   int(bool(re.search(r'012345|123456|234567|345678|456789|567890|678901', digits))),
        "all_same":            int(len(set(digits)) <= 2 and len(digits) > 5),
        "starts_0900":         int(digits.startswith('0900') or digits.startswith('900') or stripped_digits.startswith('900')),
        "starts_090":          int(digits.startswith('090') and not digits.startswith('0900')),
        "has_letters":         int(bool(re.search(r'[a-zA-Z]', cleaned))),
        "double_cc":           int(bool(re.search(r'^(\+00|\+\+|0000)', cleaned))),
        "is_nigerian_pattern": int(digits.startswith('234') or digits.startswith('00234')),
    }


def _generate_fraud_numbers(n=1000):
    numbers = []

    # Belgian/Dutch premium rate
    be_pfx = ["090"]
    nl_pfx = ["090", "091", "092", "093"]
    for pfx in be_pfx:
        for _ in range(n // 20):
            numbers.append(f"+32{pfx}{''.join([str(random.randint(0,9)) for _ in range(6)])}")
    for pfx in nl_pfx:
        for _ in range(n // 20):
            numbers.append(f"+31{pfx}{''.join([str(random.randint(0,9)) for _ in range(6)])}")

    # Caribbean callback scam codes
    for cc in ["1473", "1876", "1268", "1649"]:
        for _ in range(n // 10):
            numbers.append(f"+{cc}{''.join([str(random.randint(0,9)) for _ in range(7)])}")

    # Nigerian numbers
    for _ in range(n // 8):
        numbers.append(f"+234{''.join([str(random.randint(0,9)) for _ in range(10)])}")

    # 0900 premium (intl format)
    for _ in range(n // 8):
        numbers.append(f"0900{''.join([str(random.randint(0,9)) for _ in range(4)])}")

    # Caller ID spoofing patterns
    for _ in range(n // 10):
        numbers.append(f"00{''.join([str(random.randint(0,9)) for _ in range(11)])}")

    # Repeating digits (fake/spoofed)
    for d in range(10):
        for _ in range(n // 50):
            length = random.randint(10, 12)
            numbers.append(str(d) * length)

    return numbers[:n]


def _generate_legit_numbers(n=1000):
    numbers = []

    # Belgian landlines and mobiles
    for _ in range(n // 4):
        numbers.append(f"+3249{''.join([str(random.randint(0,9)) for _ in range(7)])}")
    for _ in range(n // 8):
        numbers.append(f"+3202{''.join([str(random.randint(0,9)) for _ in range(7)])}")

    # Dutch numbers
    for _ in range(n // 4):
        numbers.append(f"+3106{''.join([str(random.randint(0,9)) for _ in range(8)])}")

    # UK numbers
    for _ in range(n // 6):
        numbers.append(f"+44{''.join([str(random.randint(0,9)) for _ in range(10)])}")

    # Generic international
    for cc in ["32", "31", "49", "33", "34"]:
        for _ in range(n // 20):
            numbers.append(f"+{cc}{''.join([str(random.randint(0,9)) for _ in range(9)])}")

    return numbers[:n]


def train():
    print("Training phone fraud classifier...")

    fraud_nums = _generate_fraud_numbers(1500)
    legit_nums = _generate_legit_numbers(1500)

    print(f"  {len(fraud_nums)} fraud numbers | {len(legit_nums)} legit numbers")

    all_nums   = fraud_nums + legit_nums
    all_labels = [1] * len(fraud_nums) + [0] * len(legit_nums)

    features = [extract_phone_features(n) for n in all_nums]
    df = pd.DataFrame(features)
    feature_cols = list(df.columns)

    X = df[feature_cols].values
    y = np.array(all_labels)

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )

    model = RandomForestClassifier(
        n_estimators=200,
        max_depth=10,
        class_weight="balanced",
        random_state=42,
        n_jobs=-1,
    )
    model.fit(X_train, y_train)

    y_pred  = model.predict(X_test)
    y_proba = model.predict_proba(X_test)[:, 1]

    cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
    cv_f1 = cross_val_score(model, X, y, cv=cv, scoring="f1")

    print(classification_report(y_test, y_pred, target_names=["Legit", "Fraud"]))
    print(f"  ROC-AUC:        {roc_auc_score(y_test, y_proba):.4f}")
    print(f"  F1 (fraud):     {f1_score(y_test, y_pred):.4f}")
    print(f"  CV F1 (5-fold): {cv_f1.mean():.4f} +/- {cv_f1.std():.4f}")

    os.makedirs("models", exist_ok=True)
    joblib.dump(model,        MODEL_PATH)
    joblib.dump(feature_cols, FEATS_PATH)
    print(f"\n  Model saved: {MODEL_PATH}")


if __name__ == "__main__":
    train()
