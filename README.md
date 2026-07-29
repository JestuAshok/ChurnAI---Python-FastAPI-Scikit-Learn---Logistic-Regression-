# 📊 ChurnAI: Telco Customer Churn Prediction & Retention Analytics Platform

![Python](https://img.shields.io/badge/Python-3.10%2B-blue?style=for-the-badge&logo=python)
![FastAPI](https://img.shields.io/badge/FastAPI-0.100%2B-009688?style=for-the-badge&logo=fastapi)
![Scikit-Learn](https://img.shields.io/badge/scikit--learn-1.0%2B-F7931E?style=for-the-badge&logo=scikit-learn)
![SQLite](https://img.shields.io/badge/SQLite-SQLAlchemy-003B57?style=for-the-badge&logo=sqlite)
![GitHub](https://img.shields.io/badge/GitHub-JestuAshok%2FChurnAI-181717?style=for-the-badge&logo=github)
![License](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)

An end-to-end Machine Learning web platform designed to predict customer churn probability, identify high-risk accounts in telecom subscriber bases, generate real-time actionable retention recommendations, and visualize strategic churn analytics.

---

## 🎯 Executive Summary

Customer churn is one of the most critical metrics for subscription-based telecommunication providers. Retaining an existing customer is significantly more cost-effective than acquiring a new one. 

**ChurnAI** bridges machine learning model training with an enterprise-ready full-stack application. It leverages engineered domain features, a tuned probability threshold classifier, SQLite historical audit logging, and an interactive executive web dashboard for real-time risk assessment and retention strategy execution.

---

## ✨ Key Features

- 🔮 **Real-Time Machine Learning Prediction**: Instant evaluation of customer churn risk percentage, risk level category (*Low Risk*, *Medium Risk*, *High Risk*), and classification outcome.
- 💡 **Actionable Retention Recommendations**: Dynamically generates tailored retention strategies based on contract type, internet service, monthly spend, and tenure.
- ⚙️ **Domain Feature Engineering**: Automatically derives advanced metrics such as Customer Lifetime Value (CLV), Service Depth Count, Average Monthly Spend, and Contract Risk Flags.
- 📊 **Executive Analytics Suite**: Dynamic dashboard featuring churn distribution, contract breakdown, monthly charge distributions, feature importances, and tenure analytics powered by Chart.js.
- 📜 **Historical Audit Trail**: SQLite database integration storing every prediction query with inputs, timestamp, generated customer IDs (`CHURN-100x`), and outcome history.
- 💻 **Standalone CLI & Automated Tests**: CLI script (`predict_custom.py`) for custom evaluations and test coverage (`backend/test_predict.py`).

---

## 🏗️ Project Architecture & Structure

```
ChurnAI/
├── backend/
│   ├── database.py         # SQLite connection & SQLAlchemy ORM model
│   ├── main.py             # FastAPI REST endpoints & static file serving
│   ├── models.py           # Pydantic input/output validation schemas
│   ├── predict.py          # ML feature engineering & inference pipeline
│   ├── requirements.txt    # Backend Python dependencies
│   └── test_predict.py     # Automated unit & integration tests
├── frontend/
│   ├── css/                # Custom CSS design system
│   ├── js/                 # Vanilla JS dashboard logic & Chart.js integration
│   ├── index.html          # Executive Dashboard & KPIs overview
│   ├── predict.html        # Interactive Single Customer Churn Calculator
│   ├── analytics.html      # Deep-dive exploratory & model feature analytics
│   ├── history.html        # Historical prediction audit records
│   └── about.html          # System methodology & architecture docs
├── models/
│   ├── churn_model.pkl     # Serialized Logistic Regression Classifier
│   ├── scaler.pkl          # StandardScaler instance for numerical normalization
│   ├── feature_names.pkl   # Exact input feature matrix column order
│   └── threshold.pkl       # Optimal classification probability threshold
├── Customer churn prediction.ipynb # ML Training, EDA & Model Tuning Notebook
├── Dataset.csv             # IBM Telco Customer Churn Dataset (Kaggle)
├── predict_custom.py       # Standalone CLI customer prediction script
└── README.md               # Complete project documentation
```

---

## 🛠️ Step-by-Step Technical Implementation

### 1. Exploratory Data Analysis & Preprocessing
- **Dataset**: [IBM Telco Customer Churn Dataset on Kaggle](https://www.kaggle.com/datasets/blastchar/telco-customer-churn) (`Dataset.csv`), containing 7,043 customer records across demographics, account information, and subscribed services.
- **Data Cleaning**: Handled missing or blank spaces in `TotalCharges`, coerced numerical columns, and transformed target column `Churn` (`Yes`/`No`) into binary numeric labels (`1`/`0`).

### 2. Feature Engineering Strategy
Domain features were engineered to increase model sensitivity and predictive capability:
- **TotalCharges**: Calculated as `MonthlyCharges * tenure` (or `MonthlyCharges` if `tenure` is 0).
- **Customer Lifetime Value (CLV)**: Cumulative value generated over the subscriber lifecycle.
- **Average Monthly Spend**: Ratio of `TotalCharges / (tenure + 1)`.
- **Total Services Count**: Aggregate count of subscribed service extensions (Phone, Multiple Lines, Online Security, Online Backup, Device Protection, Tech Support, Streaming TV, Streaming Movies).
- **Long-Term Customer Flag**: Binary indicator (`1` if `tenure >= 24` months, else `0`).
- **Contract & Service Flags**: Specific indicators for month-to-month contracts and fiber optic usage.

### 3. Machine Learning Model Training & Threshold Tuning
- **Preprocessing Pipeline**: Categorical variables encoded via One-Hot Encoding (`pd.get_dummies`). Features normalized using `StandardScaler`.
- **Algorithm**: Logistic Regression trained with balanced class weights.
- **Threshold Optimization**: Rather than using a generic `0.5` probability threshold, a custom threshold (`threshold.pkl`) was saved to optimize the trade-off between Precision and Recall for churn identification.
- **Serialization**: Saved binary artifacts (`churn_model.pkl`, `scaler.pkl`, `feature_names.pkl`, `threshold.pkl`) with `joblib`.

### 4. FastAPI REST Backend Development
- Created robust Pydantic data validation schemas in `backend/models.py`.
- Developed `backend/predict.py` to ingest raw customer JSON payloads, re-apply the feature engineering pipeline, scale inputs, and execute inference with calibrated decision boundaries.
- Integrated SQLite database using SQLAlchemy (`backend/database.py`) to maintain persistent prediction audit trails.
- Configured FastAPI static mounting (`backend/main.py`) to serve both the backend API and frontend single-page web assets simultaneously.

### 5. Interactive Frontend Design
- Built a responsive UI using Vanilla JavaScript, HTML5, and custom CSS design systems.
- Integrated **Chart.js** for real-time visualization of risk distributions, feature importance rankings, contract distributions, and financial metrics.

---

## 🔌 API Endpoints Reference

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `GET` | `/health` | Server status and timestamp check |
| `POST` | `/predict` | Ingests customer payload, returns churn probability, risk level, engineered features & business recommendations |
| `GET` | `/history` | Returns historical prediction records from SQLite database |
| `GET` | `/analytics` | Aggregates dataset insights, feature importance, and model performance metrics |

### Sample Request (`POST /predict`)
```json
{
  "gender": "Female",
  "SeniorCitizen": 0,
  "Partner": "No",
  "Dependents": "No",
  "tenure": 2,
  "PhoneService": "Yes",
  "MultipleLines": "No",
  "InternetService": "Fiber optic",
  "OnlineSecurity": "No",
  "OnlineBackup": "No",
  "DeviceProtection": "No",
  "TechSupport": "No",
  "StreamingTV": "No",
  "StreamingMovies": "No",
  "Contract": "Month-to-month",
  "PaperlessBilling": "Yes",
  "PaymentMethod": "Electronic check",
  "MonthlyCharges": 85.50
}
```

### Sample Response
```json
{
  "customer_id": "CHURN-1001",
  "probability": 78.42,
  "prediction": "Churn",
  "risk_level": "High Risk",
  "engineered_features": {
    "TotalCharges": 171.0,
    "CustomerLifetimeValue": 171.0,
    "AverageMonthlySpend": 57.0,
    "TotalServices": 1,
    "LongTermCustomer": 0,
    "MonthlyContract": 1,
    "InternetServiceCount": 0
  },
  "business_recommendations": [
    "High Churn Risk (78.42%): Urgent retention intervention required.",
    "Offer 1-year or 2-year contract discount to transition away from month-to-month plan.",
    "Provide technical onboarding or complimentary TechSupport / Security features."
  ],
  "timestamp": "2026-07-24 10:30:00"
}
```

---

## 🚀 Getting Started & Running Locally

### Prerequisites
- Python 3.10 or higher
- Git

### Quickstart

1. **Clone the Repository**:
   ```bash
   git clone https://github.com/JestuAshok/ChurnAI.git
   cd ChurnAI
   ```

2. **Set Up Virtual Environment**:
   ```bash
   python -m venv .venv
   # Windows (PowerShell):
   .\.venv\Scripts\Activate.ps1
   # Linux/macOS:
   source .venv/bin/activate
   ```

3. **Install Dependencies**:
   ```bash
   pip install -r backend/requirements.txt
   ```

4. **Launch the Application**:
   ```bash
   python -m uvicorn backend.main:app --host 127.0.0.1 --port 8000 --reload
   ```

5. **Access Web Interfaces**:
   - **Executive Dashboard**: `http://127.0.0.1:8000`
   - **Interactive API Documentation (Swagger UI)**: `http://127.0.0.1:8000/docs`

---

## 🧪 Running CLI Predictions & Automated Tests

- **Execute CLI Prediction Script**:
  ```bash
  python predict_custom.py
  ```

- **Run Automated Backend Unit Tests**:
  ```bash
  pytest backend/test_predict.py
  ```

---

## 📜 License

Distributed under the [MIT License](LICENSE). Created by [Jestu Ashok](https://github.com/JestuAshok).
