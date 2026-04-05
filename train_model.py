"""
EMI Stress Tester — Model Training Script
Run this once before starting the Flask app:  python train_model.py
"""

import os
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
import joblib

RANDOM_STATE = 42
N_SAMPLES = 500

np.random.seed(RANDOM_STATE)

# ── 1. Generate synthetic dataset ────────────────────────────────────────────

monthly_income       = np.random.randint(25_000, 200_000, N_SAMPLES).astype(float)
total_emi            = (monthly_income * np.random.uniform(0.05, 0.65, N_SAMPLES)).round(2)
living_expense       = (monthly_income * np.random.uniform(0.10, 0.55, N_SAMPLES)).round(2)
total_burn           = (total_emi + living_expense).round(2)
savings              = (monthly_income * np.random.uniform(0.5, 24.0, N_SAMPLES)).round(2)
proposed_loan_amount = np.random.randint(50_000, 2_000_000, N_SAMPLES).astype(float)

emi_to_income_ratio  = (total_emi   / monthly_income * 100).round(2)
burn_to_income_ratio = (total_burn  / monthly_income * 100).round(2)
survival_months      = (savings     / total_burn).round(2)

# Deterministic default rule
defaulted = np.where(
    (burn_to_income_ratio > 70) | (survival_months < 1.5),
    1, 0
).astype(int)

# Add ~10 % random noise (flip labels)
noise_mask = np.random.rand(N_SAMPLES) < 0.10
defaulted[noise_mask] = 1 - defaulted[noise_mask]

df = pd.DataFrame({
    "monthly_income":       monthly_income,
    "total_emi":            total_emi,
    "living_expense":       living_expense,
    "total_burn":           total_burn,
    "emi_to_income_ratio":  emi_to_income_ratio,
    "burn_to_income_ratio": burn_to_income_ratio,
    "savings":              savings,
    "survival_months":      survival_months,
    "proposed_loan_amount": proposed_loan_amount,
    "defaulted":            defaulted,
})

os.makedirs("dataset", exist_ok=True)
df.to_csv("dataset/loan_data.csv", index=False)
print(f"✔  Saved dataset/loan_data.csv  ({N_SAMPLES} rows, "
      f"{defaulted.sum()} defaults / {N_SAMPLES - defaulted.sum()} non-defaults)")

# ── 2. Train Random Forest ───────────────────────────────────────────────────

FEATURES = [
    "monthly_income", "total_emi", "living_expense", "total_burn",
    "emi_to_income_ratio", "burn_to_income_ratio", "savings",
    "survival_months", "proposed_loan_amount",
]

X = df[FEATURES].values
y = df["defaulted"].values

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.20, random_state=RANDOM_STATE, stratify=y
)

model = RandomForestClassifier(n_estimators=100, random_state=RANDOM_STATE)
model.fit(X_train, y_train)

y_pred = model.predict(X_test)

print("\n── Model Evaluation ──────────────────────────────────────────")
print(f"  Accuracy  : {accuracy_score(y_test,  y_pred):.4f}")
print(f"  Precision : {precision_score(y_test, y_pred, zero_division=0):.4f}")
print(f"  Recall    : {recall_score(y_test,    y_pred, zero_division=0):.4f}")
print(f"  F1 Score  : {f1_score(y_test,        y_pred, zero_division=0):.4f}")
print("──────────────────────────────────────────────────────────────")

# ── 3. Save model ────────────────────────────────────────────────────────────

joblib.dump(model, "model.pkl")
print("\n✔  Saved model.pkl — ready to serve via Flask.\n")
