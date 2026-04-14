"""
train_email.py - Train the email phishing classifier

Datasets:
  1. SpamAssassin Public Corpus  - real ham/spam emails (auto-downloaded)
  2. Synthetic templates         - covers advance fee fraud, credential harvesting, etc.

Usage:
  python src/train_email.py
  python src/train_email.py --sample-only   # skip download, use synthetic only
"""

import os
import sys
import re
import argparse
import urllib.request
import zipfile
import io
import warnings

import pandas as pd
import numpy as np
import joblib

warnings.filterwarnings("ignore")
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from sklearn.pipeline import Pipeline
from sklearn.linear_model import LogisticRegression
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.model_selection import train_test_split, cross_val_score, StratifiedKFold
from sklearn.metrics import classification_report, roc_auc_score, f1_score

MODEL_PATH  = "models/email_model.pkl"
DATA_CACHE  = "data/emails_combined.csv"

PHISHING_TEMPLATES = [
    "Dear Customer, your account has been suspended. Verify immediately at http://paypal-login-secure.com/verify or it will be closed within 24 hours.",
    "URGENT: We detected unusual activity on your account. Click here NOW to confirm your identity: http://bank-secure-alert.net/login",
    "Congratulations! You have won a FREE iPhone 15. Claim your prize here: http://free-prize-winner.ru/claim?id=99",
    "Your Netflix subscription has expired. Update your billing details immediately: http://netflix-billing-update.com/pay",
    "Dear Valued Member, your PayPal account will be limited. Please verify your information: http://paypal.account-verify.net",
    "ACTION REQUIRED: Your Amazon account has been locked due to suspicious activity. Verify here: http://amazon-account-alert.xyz",
    "FINAL WARNING: Your bank account will be closed. Provide your credentials immediately to avoid suspension.",
    "You have a pending wire transfer of $5,000. Confirm your bank details to receive the funds today.",
    "Dear User, we detected a login from an unknown device. Confirm your password here or your account will be blocked.",
    "Congratulations! You are selected for a $1000 gift card. Enter your details to claim your reward now.",
    "Your DHL package could not be delivered. Pay the small customs fee to release it: http://dhl-customs.info/pay",
    "SECURITY ALERT: Your email password needs to be reset immediately. Click here: http://secure-password-reset.net",
    "Dear Account Holder, your credit card has been flagged for fraud. Verify your card number and PIN immediately.",
    "You have been selected for our exclusive loyalty program. Provide your social security number to enroll.",
    "Your account password expires today. Update now to avoid losing access: http://account-update-now.com/login",
    "URGENT ACTION NEEDED: Tax refund of $842 is pending. Submit your bank account details to receive it.",
    "We have placed a hold on your account due to suspicious transactions. Call us at +1-900-555-0199 immediately.",
    "Your computer has been infected with a virus! Call our support team NOW at 0900-HELPDESK to fix it.",
    "Dear winner, you have been randomly selected to receive 500 euros. Click here to claim: http://euro-lottery-win.tk",
    "Verify your identity to avoid account termination. Enter your username and password at: http://id-verify.net",
    # Advance fee fraud templates
    "Dear Beloved Friend, I know this message will come to you as a surprise but permit me of my desire to go into business relationship with you.",
    "I am the son of the late president and I have the sum of USD 15.5 million deposited in a security company. I need a reliable person to transfer the fund.",
    "Dear Trusted Partner, I write to solicit your assistance in the transfer of funds belonging to my deceased father into your bank account.",
    "This message will come to you as surprised. I am contacting you because of a sum of EUR 12 million kept in a bank here. I offer you 30% of the total sum.",
    "Dear sir/madam, permit me to introduce myself. I have civil war funds totaling USD 8 million deposited in a safety keeping. Reply to my alternative email.",
    "Dear Trusted One, I am the widow of the late minister. There is the sum of 7.5 million USD that I need to transfer out. Please reply if you are a reliable and honest person.",
    "I got your contact through the internet. I have a business proposal regarding funds transfer. I will give you 40% of the total amount if you assist me.",
    "You have been chosen to receive compensation funds from the Nigerian government. We need your bank account details to transfer USD 2.5 million.",
    "Greetings dear friend, I am a banker and I need your assistance to move the sum of USD 18 million. I will offer you 35% of the total fund. Remain blessed.",
    "I am contacting you regarding an inheritance of GBP 5.2 million left by a deceased client with no next of kin. You share the same surname. Please reply to my private email.",
]

LEGIT_TEMPLATES = [
    "Hi John, your order #45231 has been shipped and will arrive by Friday. Track it on our website.",
    "Thank you for subscribing to our newsletter. You can unsubscribe at any time using the link below.",
    "Your monthly statement is ready. Log in to your account to view your transactions from last month.",
    "Meeting reminder: Team standup tomorrow at 10:00 AM. Please review the agenda attached to this email.",
    "Your password was successfully changed. If you did not make this change, please contact support.",
    "Hi Sarah, I wanted to follow up on our conversation from yesterday about the project timeline.",
    "Your appointment is confirmed for March 15 at 2:30 PM. Please arrive 10 minutes early.",
    "Thank you for your payment of 49.99 euros. Your subscription has been renewed for another year.",
    "Your flight booking is confirmed. Please check in online 24 hours before departure.",
    "The weekly report is attached. Please review and let me know if you have any questions.",
    "Your parcel has been delivered to your mailbox. A signature was not required.",
    "Our offices will be closed on Monday for a public holiday.",
    "Your support ticket #8823 has been resolved. Please let us know if you need further assistance.",
    "Just a friendly reminder that your library books are due back next week.",
    "Your invoice for January is attached. Payment is due within 30 days.",
    "Thanks for attending our webinar. The recording is now available on our website.",
    "We wanted to let you know that your application has been received and is under review.",
    "Hi, your gym membership renewal is coming up. Here is the updated pricing for next year.",
    "Your recent transaction of 23.50 euros at Albert Heijn was processed successfully.",
    "Please find attached the minutes from last week's meeting. Let me know if anything needs correction.",
    "Reminder: your car insurance policy renews next month. No action is required unless you want to make changes.",
    "Your account summary for February is now available. Log in to view your balance and recent activity.",
    "We received your return request and will process it within 5 business days.",
    "Hi team, here is this week's sprint update. Three tickets closed, two carried over.",
    "Thank you for your feedback. We have passed it on to our product team.",
]


def _generate_synthetic(n_per_class=200):
    random = __import__('random')
    phishing = [random.choice(PHISHING_TEMPLATES) for _ in range(n_per_class)]
    legit    = [random.choice(LEGIT_TEMPLATES)    for _ in range(n_per_class)]
    labels   = [1] * n_per_class + [0] * n_per_class
    return list(zip(phishing + legit, labels))


def _load_spamassassin():
    url = "https://spamassassin.apache.org/old/publiccorpus/20030228_spam.tar.bz2"
    rows = []
    try:
        print("  Downloading SpamAssassin corpus...")
        with urllib.request.urlopen(url, timeout=30) as resp:
            data = resp.read()
        import tarfile
        with tarfile.open(fileobj=io.BytesIO(data), mode="r:bz2") as tar:
            for member in tar.getmembers()[:300]:
                f = tar.extractfile(member)
                if f:
                    try:
                        text = f.read().decode("utf-8", errors="ignore")
                        rows.append((text[:2000], 1))
                    except Exception:
                        pass
        print(f"  SpamAssassin: {len(rows)} emails loaded")
    except Exception as e:
        print(f"  SpamAssassin download failed: {e}")
    return rows


def build_dataset(sample_only=False):
    if os.path.exists(DATA_CACHE):
        print(f"  Loading cached dataset: {DATA_CACHE}")
        df = pd.read_csv(DATA_CACHE)
        return df["text"].tolist(), df["label"].tolist()

    rows = _generate_synthetic(400)

    if not sample_only:
        spam_rows = _load_spamassassin()
        rows += spam_rows

    texts  = [r[0] for r in rows]
    labels = [r[1] for r in rows]

    os.makedirs("data", exist_ok=True)
    pd.DataFrame({"text": texts, "label": labels}).to_csv(DATA_CACHE, index=False)
    print(f"  Dataset cached: {DATA_CACHE}")
    return texts, labels


def train(sample_only=False):
    print("Training email classifier...")

    texts, labels = build_dataset(sample_only)
    print(f"  {len(texts)} emails | {sum(labels)} phishing | {labels.count(0)} legit")

    X_train, X_test, y_train, y_test = train_test_split(
        texts, labels, test_size=0.2, random_state=42, stratify=labels
    )

    pipeline = Pipeline([
        ("tfidf", TfidfVectorizer(
            ngram_range=(1, 2),
            max_features=15000,
            sublinear_tf=True,
            strip_accents="unicode",
            analyzer="word",
            token_pattern=r"\b[a-zA-Z][a-zA-Z0-9]{2,}\b",
        )),
        ("clf", LogisticRegression(
            C=1.0,
            class_weight="balanced",
            max_iter=1000,
            random_state=42,
        )),
    ])

    print("Training pipeline...")
    pipeline.fit(X_train, y_train)

    y_pred  = pipeline.predict(X_test)
    y_proba = pipeline.predict_proba(X_test)[:, 1]

    cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
    cv_f1 = cross_val_score(pipeline, texts, labels, cv=cv, scoring="f1")

    print(classification_report(y_test, y_pred, target_names=["Legit", "Phishing"]))
    print(f"  ROC-AUC:        {roc_auc_score(y_test, y_proba):.4f}")
    print(f"  F1 (phishing):  {f1_score(y_test, y_pred):.4f}")
    print(f"  CV F1 (5-fold): {cv_f1.mean():.4f} +/- {cv_f1.std():.4f}")

    os.makedirs("models", exist_ok=True)
    joblib.dump(pipeline, MODEL_PATH)
    print(f"\n  Model saved: {MODEL_PATH}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--sample-only", action="store_true", help="Skip SpamAssassin download")
    args = parser.parse_args()
    train(args.sample_only)
