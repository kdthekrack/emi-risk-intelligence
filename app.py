"""
EMI Risk Intelligence — Flask Application
"""

from flask import Flask, render_template, request, jsonify
import joblib
import numpy as np
from calculator import calculate_emi, calculate_stress, get_recommended_living

app = Flask(__name__)

# Load trained model at startup
model = joblib.load("model.pkl")


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/analyze", methods=["POST"])
def analyze():
    data = request.get_json(force=True)

    # ── Parse inputs ──────────────────────────────────────────────────────────
    income          = float(data.get("income", 0))
    savings         = float(data.get("savings", 0))
    home_emi        = float(data.get("home_emi", 0))
    car_emi         = float(data.get("car_emi", 0))
    personal_emi    = float(data.get("personal_emi", 0))
    other_emi       = float(data.get("other_emi", 0))
    living_expense  = float(data.get("living_expense", 0))
    loan_amount     = float(data.get("loan_amount", 0))
    loan_rate       = float(data.get("loan_rate", 0))
    loan_tenure     = float(data.get("loan_tenure", 0))

    # ── Core calculations ─────────────────────────────────────────────────────
    new_emi              = calculate_emi(loan_amount, loan_rate, loan_tenure)
    total_current_emis   = home_emi + car_emi + personal_emi + other_emi

    stress = calculate_stress(
        income, savings, total_current_emis, living_expense, new_emi
    )

    recommended_living, safe_burn = get_recommended_living(
        savings, total_current_emis, new_emi
    )

    reduction_needed = living_expense - recommended_living

    # ── ML prediction ─────────────────────────────────────────────────────────
    # Feature order must match training: 9 features
    features = np.array([[
        income,
        total_current_emis + new_emi,      # total_emi
        living_expense,
        stress["total_burn"],
        stress["emi_to_income_ratio"],
        stress["burn_to_income_ratio"],
        savings,
        stress["survival_months"],
        loan_amount,
    ]])

    default_prob_raw = model.predict_proba(features)[0][1]  # probability of class 1
    default_prob     = round(default_prob_raw * 100, 1)

    # ── Verdict ───────────────────────────────────────────────────────────────
    if default_prob_raw < 0.35:
        verdict = "Safe"
    elif default_prob_raw < 0.65:
        verdict = "At Risk"
    else:
        verdict = "High Risk"

    # ── Build response ────────────────────────────────────────────────────────
    return jsonify({
        "new_emi":               new_emi,
        "total_current_emis":    round(total_current_emis, 2),
        "total_emis_after":      stress["total_emis_after"],
        "living_expense":        round(living_expense, 2),
        "total_burn":            stress["total_burn"],
        "burn_to_income_ratio":  stress["burn_to_income_ratio"],
        "emi_to_income_ratio":   stress["emi_to_income_ratio"],
        "survival_months":       stress["survival_months"],
        "savings_after_1m":      stress["savings_after_1m"],
        "savings_after_2m":      stress["savings_after_2m"],
        "savings_after_3m":      stress["savings_after_3m"],
        "default_probability":   default_prob,
        "verdict":               verdict,
        "recommended_living":    recommended_living,
        "reduction_needed":      round(reduction_needed, 2),
        "income":                round(income, 2),
        "savings":               round(savings, 2),
        "safe_burn":             round(safe_burn, 2),
    })


if __name__ == "__main__":
    app.run(debug=True)