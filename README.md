# ⚡ EMI Risk Intelligence — AI-Powered Financial Risk Analyzer

An AI/ML-powered personal finance system that evaluates loan affordability and simulates financial stress under income disruption.

Unlike traditional EMI calculators, this tool models **cash flow stress, survival duration, and default probability**, helping users make informed borrowing decisions.

---

## 🚨 Problem

Most individuals take loans without understanding how financial stress accumulates when income becomes unstable.

Traditional tools only show EMI values — they do not model:

* Liquidity risk (how long savings will last)
* Stress under zero income scenarios
* Probability of loan default

This leads to over-leveraging and poor financial planning.

---

## 🚀 Features

* Standard reducing-balance EMI calculator
* Financial stress simulation (1–3 months income loss)
* ML-based default probability prediction (0–100%)
* Risk classification: **Safe / At Risk / High Risk**
* Recommended safe living expense threshold
* Interactive Chart.js visualizations
* Fully responsive, zero-reload UI

---

## ⚙️ How It Works

1. **User Input**

   * Income, savings, EMIs, expenses, loan details

2. **Financial Computation**

   * Total monthly burn (EMIs + expenses)
   * EMI-to-income ratio
   * Burn-to-income ratio
   * Survival months (savings ÷ burn)

3. **Stress Simulation**

   * Projects savings depletion over 1, 2, and 3 months with zero income

4. **Machine Learning Prediction**

   * Random Forest model evaluates default probability
   * Uses engineered financial features (ratios, liquidity, loan size)

5. **Decision Layer**

   * Classifies risk level
   * Recommends maximum safe living expense

---

## 🏗️ System Architecture

```
User Input 
   ↓
Flask Backend (app.py)
   ↓
Financial Calculator (calculator.py)
   ↓
ML Model (Random Forest)
   ↓
Risk Prediction + Recommendation
   ↓
JSON Response
   ↓
Frontend (Chart.js Visualization)
```

---

## 🧪 Demo: Sample Test Values

| Field             | Value      |
| ----------------- | ---------- |
| Monthly Income    | ₹ 60,000   |
| Current Savings   | ₹ 1,20,000 |
| Home Loan EMI     | ₹ 18,000   |
| Car Loan EMI      | ₹ 8,000    |
| Personal Loan EMI | ₹ 5,000    |
| Other EMI         | ₹ 0        |
| Living Expenses   | ₹ 15,000   |
| Proposed Loan     | ₹ 3,00,000 |
| Interest Rate     | 12 %       |
| Tenure            | 36 months  |

**Expected Output (approx):**

* New EMI ≈ ₹ 9,964
* Total Burn ≈ ₹ 55,964
* Survival ≈ 2.1 months
* Default Risk ≈ 80–85%
* Verdict: **High Risk**
* Recommended Living Expense ≈ ₹ 2,000 – ₹ 9,000

---

## 🖥️ Quickstart (Local Setup)

### 1. Install dependencies

```bash
pip install -r requirements.txt
```

### 2. Train the model *(required before running app)*

```bash
python train_model.py
```

Generates:

* `dataset/loan_data.csv` (synthetic dataset)
* `model.pkl` (trained model)

### 3. Run the application

```bash
python app.py
```

Open in browser:

```
http://127.0.0.1:5000
```

---

## 🌐 Deployment (Render)

1. Push repository to GitHub
2. Go to Render → New Web Service
3. Configure:

| Setting       | Value                                                      |
| ------------- | ---------------------------------------------------------- |
| Environment   | Python 3                                                   |
| Build Command | `pip install -r requirements.txt && python train_model.py` |
| Start Command | `gunicorn app:app`                                         |

4. Deploy

> Note: Free tier sleeps after inactivity.

---

## 🧠 Why Machine Learning?

Financial risk is influenced by nonlinear interactions between:

* income
* liabilities
* expenses
* liquidity

A **Random Forest model** captures these relationships better than rule-based systems, enabling more realistic default probability estimation.

---

## 🧰 Tech Stack

| Layer      | Technology                   |
| ---------- | ---------------------------- |
| Backend    | Python, Flask, Gunicorn      |
| ML         | scikit-learn (Random Forest) |
| Data       | pandas, numpy                |
| Frontend   | HTML, CSS, Vanilla JS        |
| Charts     | Chart.js                     |
| Deployment | Render                       |

---

## ⚠️ Limitations

* Model trained on synthetic data (rule-based labeling)
* Does not include real-world credit bureau data
* Assumes constant income and expenses
* No income volatility or job stability modeling
* Limited to short-term (3-month) stress simulation

---

## 🔮 Future Improvements

* Train on real-world financial datasets
* Add explainable AI (SHAP) for risk transparency
* Introduce income variability scenarios (salary cuts, job loss probability)
* Expand simulation horizon beyond 3 months
* Convert into API-based microservice
* Add credit score estimation module

---

## 📸 Screenshots (Add These)

* UI dashboard
* Cash flow chart
* Savings depletion graph

*(Adding visuals significantly improves project impact)*

---

## 📌 Summary

This project demonstrates:

* Financial modeling (cash flow, EMI, liquidity)
* Feature engineering for risk analysis
* ML integration into real-world decision systems
* Full-stack deployment (Flask + frontend + charts)

---
