"""
EMI Stress Tester — Core Financial Calculator
"""


def calculate_emi(principal, annual_rate, tenure_months):
    """
    Standard reducing balance EMI formula:
    EMI = P * r * (1+r)^n / ((1+r)^n - 1)
    Returns 0 if principal or tenure is 0, or if rate is 0 (simple division).
    """
    if principal <= 0 or tenure_months <= 0:
        return 0.0

    if annual_rate <= 0:
        # Zero interest: divide principal evenly over tenure
        return round(principal / tenure_months, 2)

    monthly_rate = annual_rate / (12 * 100)
    factor = (1 + monthly_rate) ** tenure_months
    emi = principal * monthly_rate * factor / (factor - 1)
    return round(emi, 2)


def calculate_stress(income, savings, total_emis, living_expense, new_emi):
    """
    Computes all stress-test metrics for the user's financial profile.

    Returns a dict with:
      - total_emis_after: total_emis + new_emi
      - total_burn: total monthly outflow
      - emi_to_income_ratio: (total_emis_after / income) * 100
      - burn_to_income_ratio: (total_burn / income) * 100
      - survival_months: how long savings lasts with no income
      - savings_after_1m, _2m, _3m: savings remaining after stress months
    """
    total_emis_after = total_emis + new_emi
    total_burn = total_emis_after + living_expense

    emi_to_income_ratio = (total_emis_after / income * 100) if income > 0 else 0.0
    burn_to_income_ratio = (total_burn / income * 100) if income > 0 else 0.0

    survival_months = round(savings / total_burn, 1) if total_burn > 0 else 999.0

    savings_after = [round(savings - total_burn * i, 2) for i in range(1, 4)]

    return {
        "total_emis_after": round(total_emis_after, 2),
        "total_burn": round(total_burn, 2),
        "emi_to_income_ratio": round(emi_to_income_ratio, 2),
        "burn_to_income_ratio": round(burn_to_income_ratio, 2),
        "survival_months": survival_months,
        "savings_after_1m": savings_after[0],
        "savings_after_2m": savings_after[1],
        "savings_after_3m": savings_after[2],
    }


def get_recommended_living(savings, total_emis, new_emi, target_months=3):
    """
    Calculates the maximum safe living expense so that savings last target_months
    with zero income.

    safe_burn   = savings / target_months
    recommended = safe_burn - total_emis - new_emi

    A negative recommended value means EMIs alone exceed the safe burn rate.
    Returns (recommended, safe_burn).
    """
    safe_burn = savings / target_months if target_months > 0 else 0.0
    recommended = safe_burn - total_emis - new_emi
    return round(recommended, 2), round(safe_burn, 2)
