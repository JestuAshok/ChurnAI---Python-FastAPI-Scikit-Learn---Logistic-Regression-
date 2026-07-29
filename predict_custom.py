import sys
import os

# Ensure package context is resolved
sys.path.append(os.path.abspath(os.path.dirname(__file__)))

from backend.models import CustomerInput
from backend.predict import predict_churn

# Define your custom customer details here:
custom_customer = CustomerInput(
    gender="Female",
    SeniorCitizen=1,                      # 1 = Senior, 0 = Non-Senior
    Partner="No",                         # Yes or No
    Dependents="No",                      # Yes or No
    tenure=3,                             # Months with company
    PhoneService="Yes",                   # Yes or No
    MultipleLines="Yes",                  # Yes, No, or No phone service
    InternetService="Fiber optic",        # DSL, Fiber optic, or No
    OnlineSecurity="No",                  # Yes, No, or No internet service
    OnlineBackup="No",                    # Yes, No, or No internet service
    DeviceProtection="No",                # Yes, No, or No internet service
    TechSupport="No",                     # Yes, No, or No internet service
    StreamingTV="Yes",                    # Yes, No, or No internet service
    StreamingMovies="Yes",                # Yes, No, or No internet service
    Contract="Month-to-month",            # Month-to-month, One year, or Two year
    PaperlessBilling="Yes",               # Yes or No
    PaymentMethod="Electronic check",     # Electronic check, Mailed check, Bank transfer (automatic), or Credit card (automatic)
    MonthlyCharges=95.50                  # Monthly charge in dollars
)

# Run model prediction
prob, label, risk, engineered, recommendations = predict_churn(custom_customer)

print("=" * 60)
print("CUSTOM CUSTOMER CHURN DIAGNOSTICS")
print("=" * 60)
print(f"Churn Probability : {prob * 100:.2f}%")
print(f"Prediction Outcome: {label}")
print(f"Risk Level        : {risk}")
print("-" * 60)
print("Engineered Features:")
for k, v in engineered.items():
    print(f"  - {k}: {v}")
print("-" * 60)
print("Business Recommendations:")
for rec in recommendations:
    print(f"  - {rec}")
print("=" * 60)
