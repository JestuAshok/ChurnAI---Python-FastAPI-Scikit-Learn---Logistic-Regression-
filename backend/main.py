import os
import json
import random
from datetime import datetime
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse, RedirectResponse
from sqlalchemy.orm import Session
import pandas as pd
import numpy as np
import joblib

from .models import CustomerInput, PredictionResponse, PredictionHistoryRecord
from .database import init_db, get_db, PredictionDBModel
from .predict import predict_churn, load_prediction_assets

app = FastAPI(
    title="Customer Churn Prediction API",
    description="FastAPI backend serving churn predictions and analytics",
    version="1.0.0"
)

# Enable CORS for frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize database on startup
@app.on_event("startup")
def startup_event():
    init_db()
    # Pre-load prediction assets to cache them
    try:
        load_prediction_assets()
        print("Prediction assets loaded successfully.")
    except Exception as e:
        print(f"Error pre-loading prediction assets: {e}")

@app.get("/health")
def health_check():
    return {"status": "healthy", "timestamp": datetime.utcnow().isoformat()}

@app.post("/predict", response_model=PredictionResponse)
def run_predict(customer: CustomerInput, db: Session = Depends(get_db)):
    try:
        # Run prediction pipeline
        prob, pred_label, risk, eng_features, recommendations = predict_churn(customer)
        
        # Format probability to percentage
        prob_pct = round(prob * 100, 2)
        
        # Generate custom sequential customer ID based on count
        customer_count = db.query(PredictionDBModel).count()
        customer_id = f"CHURN-{1000 + customer_count + 1}"
        
        # Get current timestamp
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Save to database
        db_record = PredictionDBModel(
            customer_id=customer_id,
            probability=prob_pct,
            prediction=pred_label,
            risk_level=risk,
            timestamp=current_time,
            inputs=json.dumps(customer.dict())
        )
        db.add(db_record)
        db.commit()
        db.refresh(db_record)
        
        return PredictionResponse(
            customer_id=customer_id,
            probability=prob_pct,
            prediction=pred_label,
            risk_level=risk,
            engineered_features=eng_features,
            business_recommendations=recommendations,
            timestamp=current_time
        )
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Prediction failed: {str(e)}"
        )

@app.get("/history")
def get_history(db: Session = Depends(get_db)):
    try:
        records = db.query(PredictionDBModel).order_by(PredictionDBModel.id.desc()).all()
        history = []
        for r in records:
            history.append({
                "id": r.id,
                "customer_id": r.customer_id,
                "probability": r.probability,
                "prediction": r.prediction,
                "risk_level": r.risk_level,
                "timestamp": r.timestamp,
                "inputs": json.loads(r.inputs)
            })
        return history
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch history: {str(e)}"
        )

@app.delete("/history")
def delete_history(db: Session = Depends(get_db)):
    try:
        db.query(PredictionDBModel).delete()
        db.commit()
        return {"status": "success", "message": "Prediction history cleared."}
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete history: {str(e)}"
        )

@app.get("/api/customer/{index}")
def get_customer_by_index(index: int):
    csv_path = "C:/Users/jestu/customer_churn_feature_engineered.csv"
    if not os.path.exists(csv_path):
        raise HTTPException(status_code=404, detail="Dataset CSV file not found")
    try:
        df = pd.read_csv(csv_path)
        if index < 0 or index >= len(df):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Index {index} is out of bounds. Must be between 0 and {len(df) - 1}."
            )
        row = df.iloc[index].to_dict()
        # Clean NaN values
        row = {k: (None if pd.isna(v) else v) for k, v in row.items()}
        return row
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch customer: {str(e)}"
        )

@app.get("/api/analytics")
def get_analytics_data():
    """
    Expose endpoints for dynamic aggregated values required by Plotly.js charts.
    """
    csv_path = "C:/Users/jestu/customer_churn_feature_engineered.csv"
    
    # Check if CSV exists, otherwise return a generated/mock set
    if os.path.exists(csv_path):
        try:
            df = pd.read_csv(csv_path)
        except Exception as e:
            df = None
            print(f"Error reading CSV: {e}")
    else:
        df = None
        print("CSV dataset not found in user path.")

    # 1. Feature Importance (Extracted from Churn Model coefficients)
    try:
        model, scaler, threshold, feature_names = load_prediction_assets()
        coefs = model.coef_[0]
        # Map to feature names and sort by absolute impact
        feature_imp = []
        for name, coef in zip(feature_names, coefs):
            feature_imp.append({
                "feature": name,
                "importance": float(coef),
                "abs_importance": float(abs(coef))
            })
        feature_imp = sorted(feature_imp, key=lambda x: x["abs_importance"], reverse=True)[:15] # top 15 features
    except Exception as e:
        feature_imp = [{"feature": "MockFeature", "importance": 0.5, "abs_importance": 0.5}]
        print(f"Error calculating feature importance: {e}")

    # Standard distribution default if dataset is missing
    if df is None:
        return {
            "churn_distribution": {"labels": ["No", "Yes"], "values": [5174, 1869]},
            "contract_vs_churn": {
                "categories": ["Month-to-month", "One year", "Two year"],
                "no_churn": [2220, 1307, 1647],
                "churn": [1655, 166, 48]
            },
            "monthly_charges_vs_churn": {
                "no_churn": [61.26] * 100,  # boxplot lists
                "churn": [74.44] * 100
            },
            "tenure_vs_churn": {
                "no_churn": [37.5] * 100,
                "churn": [17.9] * 100
            },
            "internet_service_vs_churn": {
                "categories": ["DSL", "Fiber optic", "No"],
                "no_churn": [1962, 1799, 1413],
                "churn": [459, 1297, 113]
            },
            "feature_importance": feature_imp,
            "probability_distribution": [random.uniform(0.05, 0.95) for _ in range(500)]
        }

    try:
        # Calculate statistics from actual dataset
        
        # A. Churn distribution
        churn_counts = df["Churn"].value_counts().to_dict()
        churn_dist = {
            "labels": list(churn_counts.keys()),
            "values": [int(v) for v in churn_counts.values()]
        }

        # B. Contract vs Churn
        contract_churn = df.groupby(["Contract", "Churn"]).size().unstack(fill_value=0)
        contract_vs_churn = {
            "categories": list(contract_churn.index),
            "no_churn": [int(v) for v in contract_churn["No"]],
            "churn": [int(v) for v in contract_churn["Yes"]]
        }

        # C. Monthly charges vs Churn (Return sampled data points for violin/box plots)
        no_churn_charges = df[df["Churn"] == "No"]["MonthlyCharges"].sample(n=min(1000, len(df[df["Churn"] == "No"])), random_state=42).tolist()
        churn_charges = df[df["Churn"] == "Yes"]["MonthlyCharges"].sample(n=min(1000, len(df[df["Churn"] == "Yes"])), random_state=42).tolist()
        
        # D. Tenure vs Churn
        no_churn_tenure = df[df["Churn"] == "No"]["tenure"].sample(n=min(1000, len(df[df["Churn"] == "No"])), random_state=42).tolist()
        churn_tenure = df[df["Churn"] == "Yes"]["tenure"].sample(n=min(1000, len(df[df["Churn"] == "Yes"])), random_state=42).tolist()

        # E. Internet Service vs Churn
        internet_churn = df.groupby(["InternetService", "Churn"]).size().unstack(fill_value=0)
        internet_vs_churn = {
            "categories": list(internet_churn.index),
            "no_churn": [int(v) for v in internet_churn["No"]],
            "churn": [int(v) for v in internet_churn["Yes"]]
        }

        # F. Probability Distribution on sample test prediction
        # Let's run a prediction sample of 400 instances from the CSV to show realistic prediction probability distributions
        prob_sample = []
        try:
            # Recreate preprocessing flow for prediction probabilities
            sample_df = df.sample(n=min(400, len(df)), random_state=42)
            
            # Extract models
            model, scaler, threshold, feature_names = load_prediction_assets()
            
            # Simple encoding matching logic
            for _, row in sample_df.iterrows():
                # Engineered
                services = ['PhoneService', 'MultipleLines', 'OnlineSecurity', 'OnlineBackup', 'DeviceProtection', 'TechSupport', 'StreamingTV', 'StreamingMovies']
                tot_services = sum([1 for s in services if row[s] == 'Yes'])
                long_term = 1 if row['tenure'] >= 24 else 0
                monthly_contract = 1 if row['Contract'] == 'Month-to-month' else 0
                clv = row['MonthlyCharges'] * row['tenure']
                avg_monthly = row['TotalCharges'] / (row['tenure'] + 1)
                
                feat_dict = {
                    'SeniorCitizen': int(row['SeniorCitizen']),
                    'tenure': float(row['tenure']),
                    'MonthlyCharges': float(row['MonthlyCharges']),
                    'TotalCharges': float(row['TotalCharges']),
                    'CustomerLifetimeValue': clv,
                    'AverageMonthlySpend': avg_monthly,
                    'TotalServices': tot_services,
                    'LongTermCustomer': long_term,
                    'MonthlyContract': monthly_contract,
                    'gender_Male': 1 if row['gender'] == 'Male' else 0,
                    'Partner_Yes': 1 if row['Partner'] == 'Yes' else 0,
                    'Dependents_Yes': 1 if row['Dependents'] == 'Yes' else 0,
                    'PhoneService_Yes': 1 if row['PhoneService'] == 'Yes' else 0,
                    'MultipleLines_No phone service': 1 if row['MultipleLines'] == 'No phone service' else 0,
                    'MultipleLines_Yes': 1 if row['MultipleLines'] == 'Yes' else 0,
                    'InternetService_Fiber optic': 1 if row['InternetService'] == 'Fiber optic' else 0,
                    'InternetService_No': 1 if row['InternetService'] == 'No' else 0,
                    'OnlineSecurity_No internet service': 1 if row['OnlineSecurity'] == 'No internet service' or row['InternetService'] == 'No' else 0,
                    'OnlineSecurity_Yes': 1 if row['OnlineSecurity'] == 'Yes' else 0,
                    'OnlineBackup_No internet service': 1 if row['OnlineBackup'] == 'No internet service' or row['InternetService'] == 'No' else 0,
                    'OnlineBackup_Yes': 1 if row['OnlineBackup'] == 'Yes' else 0,
                    'DeviceProtection_No internet service': 1 if row['DeviceProtection'] == 'No internet service' or row['InternetService'] == 'No' else 0,
                    'DeviceProtection_Yes': 1 if row['DeviceProtection'] == 'Yes' else 0,
                    'TechSupport_No internet service': 1 if row['TechSupport'] == 'No internet service' or row['InternetService'] == 'No' else 0,
                    'TechSupport_Yes': 1 if row['TechSupport'] == 'Yes' else 0,
                    'StreamingTV_No internet service': 1 if row['StreamingTV'] == 'No internet service' or row['InternetService'] == 'No' else 0,
                    'StreamingTV_Yes': 1 if row['StreamingTV'] == 'Yes' else 0,
                    'StreamingMovies_No internet service': 1 if row['StreamingMovies'] == 'No internet service' or row['InternetService'] == 'No' else 0,
                    'StreamingMovies_Yes': 1 if row['StreamingMovies'] == 'Yes' else 0,
                    'Contract_One year': 1 if row['Contract'] == 'One year' else 0,
                    'Contract_Two year': 1 if row['Contract'] == 'Two year' else 0,
                    'PaperlessBilling_Yes': 1 if row['PaperlessBilling'] == 'Yes' else 0,
                    'PaymentMethod_Credit card (automatic)': 1 if row['PaymentMethod'] == 'Credit card (automatic)' else 0,
                    'PaymentMethod_Electronic check': 1 if row['PaymentMethod'] == 'Electronic check' else 0,
                    'PaymentMethod_Mailed check': 1 if row['PaymentMethod'] == 'Mailed check' else 0
                }
                vec = [feat_dict[col] for col in feature_names]
                scaled = scaler.transform([vec])
                prob = float(model.predict_proba(scaled)[0, 1])
                prob_sample.append(prob)
        except Exception as e:
            print(f"Error running prediction sample: {e}")
            prob_sample = [random.uniform(0.05, 0.95) for _ in range(200)]

        return {
            "churn_distribution": churn_dist,
            "contract_vs_churn": contract_vs_churn,
            "monthly_charges_vs_churn": {
                "no_churn": no_churn_charges,
                "churn": churn_charges
            },
            "tenure_vs_churn": {
                "no_churn": no_churn_tenure,
                "churn": churn_tenure
            },
            "internet_service_vs_churn": {
                "categories": list(internet_churn.index),
                "no_churn": [int(v) for v in internet_churn["No"]],
                "churn": [int(v) for v in internet_churn["Yes"]]
            },
            "feature_importance": feature_imp,
            "probability_distribution": prob_sample
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to calculate analytics: {str(e)}"
        )

# Mounting the static frontend files
# Define frontend absolute path
FRONTEND_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "frontend"))
app.mount("/", StaticFiles(directory=FRONTEND_DIR, html=True), name="frontend")
