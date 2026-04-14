"""
train.py - Train the URL phishing classifier

Usage:
    python src/train.py --data data/sample_urls.csv
    python src/train.py --data data/malicious_phish.csv
"""

import argparse
import os
import sys
import pandas as pd
import joblib
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split, cross_val_score, StratifiedKFold
from sklearn.metrics import classification_report, roc_auc_score, f1_score

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from src.features import extract_features, FEATURE_COLS

MODEL_OUTPUT = "models/arcticsecurityshield.pkl"


def load_dataset(path: str) -> pd.DataFrame:
    df = pd.read_csv(path)

    if "url" in df.columns and "type" in df.columns:
        print(f"  Extracting features from URLs...")
        features = df["url"].apply(extract_features)
        df_feat = pd.DataFrame(features.tolist())
        df_feat["label"] = (df["type"] == "phishing").astype(int)
        return df_feat
    elif "label" in df.columns:
        print(f"  Using pre-extracted features.")
        return df
    else:
        raise ValueError(f"CSV must have columns [url, type] or {FEATURE_COLS + ['label']}")


def train(data_path: str):
    print("Training URL classifier...")

    print(f"\n[1/4] Loading: {data_path}")
    df = load_dataset(data_path)
    print(f"  {len(df)} rows | {df['label'].sum()} phishing | {(df['label']==0).sum()} benign")

    print("\n[2/4] Train/test split (80/20, stratified)")
    X = df[FEATURE_COLS]
    y = df["label"]
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )

    print("\n[3/4] Training Random Forest...")
    model = RandomForestClassifier(
        n_estimators=200,
        max_depth=15,
        min_samples_split=5,
        min_samples_leaf=2,
        class_weight="balanced",
        random_state=42,
        n_jobs=-1,
    )
    model.fit(X_train, y_train)
    print("  Done.")

    print("\n[4/4] Evaluation")
    y_pred  = model.predict(X_test)
    y_proba = model.predict_proba(X_test)[:, 1]

    cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
    cv_f1 = cross_val_score(model, X, y, cv=cv, scoring="f1")

    print(classification_report(y_test, y_pred, target_names=["Benign", "Phishing"]))
    print(f"  ROC-AUC:        {roc_auc_score(y_test, y_proba):.4f}")
    print(f"  F1 (phishing):  {f1_score(y_test, y_pred):.4f}")
    print(f"  CV F1 (5-fold): {cv_f1.mean():.4f} +/- {cv_f1.std():.4f}")

    os.makedirs("models", exist_ok=True)
    joblib.dump(model, MODEL_OUTPUT)
    print(f"\n  Model saved: {MODEL_OUTPUT}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--data", default="data/sample_urls.csv")
    args = parser.parse_args()
    train(args.data)
