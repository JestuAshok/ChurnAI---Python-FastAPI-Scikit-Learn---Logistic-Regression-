import os
import joblib
import pandas as pd
import numpy as np
from typing import Dict, Any, Tuple, List
from .models import CustomerInput

# Get absolute path to models directory
MODELS_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "models"))

# Cache model objects in memory
_model = None
_scaler = None
_threshold = None
_feature_names = None

def load_prediction_assets():
    global _model, _scaler, _threshold, _feature_names
    if _model is None:
        model_path = os.path.join(MODELS_DIR, "churn_model.pkl")
        scaler_path = os.path.join(MODELS_DIR, "scaler.pkl")
        threshold_path = os.path.join(MODELS_DIR, "threshold.pkl")
        features_path = os.path.join(MODELS_DIR, "feature_names.pkl")

        if not all(os.path.exists(p) for p in [model_path, scaler_path, threshold_path, features_path]):
            raise FileNotFoundError("One or more model pickle files are missing in backend/models.")

        _model = joblib.load(model_path)
        _scaler = joblib.load(scaler_path)
        _threshold = float(joblib.load(threshold_path))
        _feature_names = joblib.load(features_path)

    return _model, _scaler, _threshold, _feature_names

def calculate_engineered_features(customer: CustomerInput) -> Dict[str, Any]:
    """
    Perform the same feature engineering logic used during model training.
    """
    # TotalCharges = MonthlyCharges * tenure (or default to MonthlyCharges if tenure is 0)
    total_charges = float(customer.MonthlyCharges * customer.tenure)
    if customer.tenure == 0:
        total_charges = float(customer.MonthlyCharges)

    # Customer Lifetime Value: CLV = MonthlyCharges * tenure
    clv = float(customer.MonthlyCharges * customer.tenure)

    # AverageMonthlySpend = TotalCharges / (tenure + 1)
    avg_monthly_spend = float(total_charges / (customer.tenure + 1))

    # TotalServices: phone service, multiple lines, and internet-based services (if Yes)
    service_columns = [
        customer.PhoneService,
        customer.MultipleLines,
        customer.OnlineSecurity,
        customer.OnlineBackup,
        customer.DeviceProtection,
        customer.TechSupport,
        customer.StreamingTV,
        customer.StreamingMovies
    ]
    total_services = sum(1 for service in service_columns if service == "Yes")

    # LongTermCustomer = 1 if tenure >= 24 else 0
    long_term_customer = 1 if customer.tenure >= 24 else 0

    # MonthlyContract = 1 if Contract == Month-to-month else 0
    monthly_contract = 1 if customer.Contract == "Month-to-month" else 0

    # InternetServiceCount: count of internet sub-services (excluding connection itself) that are 'Yes'
    internet_subservices = [
        customer.OnlineSecurity,
        customer.OnlineBackup,
        customer.DeviceProtection,
        customer.TechSupport,
        customer.StreamingTV,
        customer.StreamingMovies
    ]
    internet_service_count = sum(1 for s in internet_subservices if s == "Yes")

    return {
        "TotalCharges": total_charges,
        "CustomerLifetimeValue": clv,
        "AverageMonthlySpend": avg_monthly_spend,
        "TotalServices": total_services,
        "LongTermCustomer": long_term_customer,
        "MonthlyContract": monthly_contract,
        "InternetServiceCount": internet_service_count
    }

def construct_feature_vector(customer: CustomerInput, eng: Dict[str, Any], feature_names: List[str]) -> List[float]:
    """
    Maps the raw inputs and engineered features to the exact dummy variables expected by the model.
    """
    # Mapping dictionary matching feature names
    feat_dict = {
        'SeniorCitizen': int(customer.SeniorCitizen),
        'tenure': float(customer.tenure),
        'MonthlyCharges': float(customer.MonthlyCharges),
        'TotalCharges': float(eng['TotalCharges']),
        'CustomerLifetimeValue': float(eng['CustomerLifetimeValue']),
        'AverageMonthlySpend': float(eng['AverageMonthlySpend']),
        'TotalServices': float(eng['TotalServices']),
        'LongTermCustomer': float(eng['LongTermCustomer']),
        'MonthlyContract': float(eng['MonthlyContract']),
        'gender_Male': 1 if customer.gender == 'Male' else 0,
        'Partner_Yes': 1 if customer.Partner == 'Yes' else 0,
        'Dependents_Yes': 1 if customer.Dependents == 'Yes' else 0,
        'PhoneService_Yes': 1 if customer.PhoneService == 'Yes' else 0,
        
        'MultipleLines_No phone service': 1 if customer.MultipleLines == 'No phone service' else 0,
        'MultipleLines_Yes': 1 if customer.MultipleLines == 'Yes' else 0,
        
        'InternetService_Fiber optic': 1 if customer.InternetService == 'Fiber optic' else 0,
        'InternetService_No': 1 if customer.InternetService == 'No' else 0,
        
        'OnlineSecurity_No internet service': 1 if customer.OnlineSecurity == 'No internet service' or customer.InternetService == 'No' else 0,
        'OnlineSecurity_Yes': 1 if customer.OnlineSecurity == 'Yes' else 0,
        
        'OnlineBackup_No internet service': 1 if customer.OnlineBackup == 'No internet service' or customer.InternetService == 'No' else 0,
        'OnlineBackup_Yes': 1 if customer.OnlineBackup == 'Yes' else 0,
        
        'DeviceProtection_No internet service': 1 if customer.DeviceProtection == 'No internet service' or customer.InternetService == 'No' else 0,
        'DeviceProtection_Yes': 1 if customer.DeviceProtection == 'Yes' else 0,
        
        'TechSupport_No internet service': 1 if customer.TechSupport == 'No internet service' or customer.InternetService == 'No' else 0,
        'TechSupport_Yes': 1 if customer.TechSupport == 'Yes' else 0,
        
        'StreamingTV_No internet service': 1 if customer.StreamingTV == 'No internet service' or customer.InternetService == 'No' else 0,
        'StreamingTV_Yes': 1 if customer.StreamingTV == 'Yes' else 0,
        
        'StreamingMovies_No internet service': 1 if customer.StreamingMovies == 'No internet service' or customer.InternetService == 'No' else 0,
        'StreamingMovies_Yes': 1 if customer.StreamingMovies == 'Yes' else 0,
        
        'Contract_One year': 1 if customer.Contract == 'One year' else 0,
        'Contract_Two year': 1 if customer.Contract == 'Two year' else 0,
        
        'PaperlessBilling_Yes': 1 if customer.PaperlessBilling == 'Yes' else 0,
        
        'PaymentMethod_Credit card (automatic)': 1 if customer.PaymentMethod == 'Credit card (automatic)' else 0,
        'PaymentMethod_Electronic check': 1 if customer.PaymentMethod == 'Electronic check' else 0,
        'PaymentMethod_Mailed check': 1 if customer.PaymentMethod == 'Mailed check' else 0
    }

    # Reorder vector to exactly match feature_names
    vector = []
    for col in feature_names:
        if col in feat_dict:
            vector.append(feat_dict[col])
        else:
            # Fallback
            vector.append(0.0)
            
    return vector

def predict_churn(customer: CustomerInput) -> Tuple[float, str, str, Dict[str, Any], List[str]]:
    """
    Loads models, pre-processes the inputs, performs inference, maps outputs, and returns recommendations.
    """
    model, scaler, threshold, feature_names = load_prediction_assets()

    # 1. Feature Engineering
    engineered = calculate_engineered_features(customer)

    # 2. Build feature vector
    feat_vector = construct_feature_vector(customer, engineered, feature_names)

    # 3. Apply standard scaler
    # Needs to be 2D array: (1, 35)
    feat_vector_scaled = scaler.transform([feat_vector])

    # 4. Predict Churn Probability
    probability = float(model.predict_proba(feat_vector_scaled)[0, 1])

    # 5. Apply threshold to get binary prediction
    # Likely to Churn if prob >= threshold else Not Likely
    is_churn = probability >= threshold
    prediction_label = "Likely to Churn" if is_churn else "Not Likely to Churn"

    # 6. Risk Level
    # 0-40%: Low, 40-70%: Medium, 70-100%: High
    probability_pct = probability * 100
    if probability_pct < 40.0:
        risk_level = "Low"
    elif probability_pct < 70.0:
        risk_level = "Medium"
    else:
        risk_level = "High"

    # 7. Generate Recommendations
    recommendations = []
    if risk_level == "High":
        recommendations.extend([
            "Offer loyalty discount (e.g. 15% off monthly bill)",
            "Upgrade to a yearly contract with locking rate",
            "Route to Priority Customer Support queue",
            "Assign dedicated Relationship Manager"
        ])
    elif risk_level == "Medium":
        recommendations.extend([
            "Offer promotional package to lock in contract",
            "Recommend bundled services (add security or backup at a discount)",
            "Initiate proactive customer satisfaction follow-up call"
        ])
    else:
        recommendations.extend([
            "Maintain regular engagement with value newsletters",
            "Reward ongoing loyalty with custom perks"
        ])

    # Add dynamic recommendation based on contract
    if customer.Contract == "Month-to-month" and risk_level in ["High", "Medium"]:
        recommendations.append("Highly Recommend: Transition from Month-to-month to a fixed-term contract.")
    
    # Add dynamic recommendation based on tech support
    if customer.InternetService != "No" and customer.TechSupport != "Yes" and risk_level in ["High", "Medium"]:
        recommendations.append("Service Alert: Recommend Tech Support add-on to resolve connectivity concerns.")

    return probability, prediction_label, risk_level, engineered, recommendations
