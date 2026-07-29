import os
import sys
import unittest
from fastapi.testclient import TestClient

# Add current workspace to python path so we can import modules
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.models import CustomerInput
from backend.predict import calculate_engineered_features, construct_feature_vector, predict_churn, load_prediction_assets
from backend.database import init_db
from backend.main import app

class TestChurnPrediction(unittest.TestCase):

    def setUp(self):
        init_db()
        # Set up a sample customer payload
        self.sample_customer = CustomerInput(
            gender="Female",
            SeniorCitizen=0,
            Partner="Yes",
            Dependents="No",
            tenure=1,
            PhoneService="No",
            MultipleLines="No phone service",
            InternetService="DSL",
            OnlineSecurity="No",
            OnlineBackup="Yes",
            DeviceProtection="No",
            TechSupport="No",
            StreamingTV="No",
            StreamingMovies="No",
            Contract="Month-to-month",
            PaperlessBilling="Yes",
            PaymentMethod="Electronic check",
            MonthlyCharges=29.85
        )

    def test_feature_assets_load(self):
        """Test that model, scaler, threshold, and feature names load correctly."""
        model, scaler, threshold, feature_names = load_prediction_assets()
        self.assertIsNotNone(model)
        self.assertIsNotNone(scaler)
        self.assertIsInstance(threshold, float)
        self.assertEqual(len(feature_names), 35)

    def test_feature_engineering_calculations(self):
        """Test feature engineering outputs for known sample."""
        eng = calculate_engineered_features(self.sample_customer)
        
        # MonthlyCharges=29.85, tenure=1
        # TotalCharges = 29.85 * 1 = 29.85
        # CLV = 29.85 * 1 = 29.85
        # AverageMonthlySpend = 29.85 / (1 + 1) = 14.925
        # TotalServices: 'Yes' in PhoneService (No), MultipleLines (No phone service), 
        # OnlineSecurity (No), OnlineBackup (Yes), DeviceProtection (No), TechSupport (No), 
        # StreamingTV (No), StreamingMovies (No) -> Total = 1 (OnlineBackup)
        
        self.assertAlmostEqual(eng["TotalCharges"], 29.85)
        self.assertAlmostEqual(eng["CustomerLifetimeValue"], 29.85)
        self.assertAlmostEqual(eng["AverageMonthlySpend"], 14.925)
        self.assertEqual(eng["TotalServices"], 1)
        self.assertEqual(eng["LongTermCustomer"], 0)
        self.assertEqual(eng["MonthlyContract"], 1)
        self.assertEqual(eng["InternetServiceCount"], 1) # OnlineBackup is Yes

    def test_feature_vector_mapping(self):
        """Test mapping raw/engineered features to standard 35-dim vector."""
        model, scaler, threshold, feature_names = load_prediction_assets()
        eng = calculate_engineered_features(self.sample_customer)
        vec = construct_feature_vector(self.sample_customer, eng, feature_names)
        
        self.assertEqual(len(vec), 35)
        # Check indices mapping
        # gender_Male should be 0 because gender is Female
        self.assertEqual(vec[feature_names.index("gender_Male")], 0)
        # Partner_Yes should be 1 because Partner is Yes
        self.assertEqual(vec[feature_names.index("Partner_Yes")], 1)
        # PhoneService_Yes should be 0 because PhoneService is No
        self.assertEqual(vec[feature_names.index("PhoneService_Yes")], 0)
        # MultipleLines_No phone service should be 1
        self.assertEqual(vec[feature_names.index("MultipleLines_No phone service")], 1)
        # MultipleLines_Yes should be 0
        self.assertEqual(vec[feature_names.index("MultipleLines_Yes")], 0)
        # InternetService_Fiber optic should be 0
        self.assertEqual(vec[feature_names.index("InternetService_Fiber optic")], 0)
        # InternetService_No should be 0
        self.assertEqual(vec[feature_names.index("InternetService_No")], 0)
        # OnlineBackup_Yes should be 1
        self.assertEqual(vec[feature_names.index("OnlineBackup_Yes")], 1)

    def test_churn_pipeline_prediction(self):
        """Test full prediction pipeline return types."""
        prob, label, risk, eng, recs = predict_churn(self.sample_customer)
        
        self.assertTrue(0.0 <= prob <= 1.0)
        self.assertIn(label, ["Likely to Churn", "Not Likely to Churn"])
        self.assertIn(risk, ["Low", "Medium", "High"])
        self.assertIsInstance(eng, dict)
        self.assertIsInstance(recs, list)
        self.assertTrue(len(recs) > 0)


class TestAPIEndpoints(unittest.TestCase):

    def setUp(self):
        init_db()
        self.client = TestClient(app)

    def test_health_endpoint(self):
        response = self.client.get("/health")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["status"], "healthy")

    def test_history_crud_flow(self):
        # 1. Clear database first
        del_resp = self.client.delete("/history")
        self.assertEqual(del_resp.status_code, 200)

        # 2. History should be empty
        hist_resp = self.client.get("/history")
        self.assertEqual(hist_resp.status_code, 200)
        self.assertEqual(len(hist_resp.json()), 0)

        # 3. Post a prediction
        payload = {
            "gender": "Female",
            "SeniorCitizen": 0,
            "Partner": "Yes",
            "Dependents": "No",
            "tenure": 1,
            "PhoneService": "No",
            "MultipleLines": "No phone service",
            "InternetService": "DSL",
            "OnlineSecurity": "No",
            "OnlineBackup": "Yes",
            "DeviceProtection": "No",
            "TechSupport": "No",
            "StreamingTV": "No",
            "StreamingMovies": "No",
            "Contract": "Month-to-month",
            "PaperlessBilling": "Yes",
            "PaymentMethod": "Electronic check",
            "MonthlyCharges": 29.85
        }
        pred_resp = self.client.post("/predict", json=payload)
        self.assertEqual(pred_resp.status_code, 200)
        pred_data = pred_resp.json()
        self.assertIn("customer_id", pred_data)
        self.assertIn("probability", pred_data)
        self.assertIn("risk_level", pred_data)

        # 4. Check history size has increased to 1
        hist_resp = self.client.get("/history")
        self.assertEqual(hist_resp.status_code, 200)
        self.assertEqual(len(hist_resp.json()), 1)
        self.assertEqual(hist_resp.json()[0]["customer_id"], pred_data["customer_id"])

    def test_analytics_endpoint(self):
        response = self.client.get("/api/analytics")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("churn_distribution", data)
        self.assertIn("contract_vs_churn", data)
        self.assertIn("monthly_charges_vs_churn", data)
        self.assertIn("tenure_vs_churn", data)
        self.assertIn("feature_importance", data)
        self.assertIn("probability_distribution", data)

    def test_customer_by_index_endpoint(self):
        response = self.client.get("/api/customer/100")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["gender"], "Male")
        self.assertEqual(data["MonthlyCharges"], 20.2)
        
        # Test out of bounds index
        response_oob = self.client.get("/api/customer/999999")
        self.assertEqual(response_oob.status_code, 400)

if __name__ == "__main__":
    unittest.main()
