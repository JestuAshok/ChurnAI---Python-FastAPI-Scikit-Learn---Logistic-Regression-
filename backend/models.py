from pydantic import BaseModel, Field, field_validator
from typing import Dict, Any, Optional
from datetime import datetime

class CustomerInput(BaseModel):
    gender: str = Field(..., description="Gender: Male or Female")
    SeniorCitizen: int = Field(..., description="Senior Citizen status: 0 or 1")
    Partner: str = Field(..., description="Partner status: Yes or No")
    Dependents: str = Field(..., description="Dependents status: Yes or No")
    tenure: int = Field(..., ge=0, description="Tenure in months")
    PhoneService: str = Field(..., description="Phone service status: Yes or No")
    MultipleLines: str = Field(..., description="Multiple lines: Yes, No, or No phone service")
    InternetService: str = Field(..., description="Internet service provider: DSL, Fiber optic, or No")
    OnlineSecurity: str = Field(..., description="Online security: Yes, No, or No internet service")
    OnlineBackup: str = Field(..., description="Online backup: Yes, No, or No internet service")
    DeviceProtection: str = Field(..., description="Device protection: Yes, No, or No internet service")
    TechSupport: str = Field(..., description="Tech support: Yes, No, or No internet service")
    StreamingTV: str = Field(..., description="Streaming TV: Yes, No, or No internet service")
    StreamingMovies: str = Field(..., description="Streaming movies: Yes, No, or No internet service")
    Contract: str = Field(..., description="Contract term: Month-to-month, One year, or Two year")
    PaperlessBilling: str = Field(..., description="Paperless billing: Yes or No")
    PaymentMethod: str = Field(..., description="Payment method: Electronic check, Mailed check, Bank transfer (automatic), or Credit card (automatic)")
    MonthlyCharges: float = Field(..., ge=0, description="Monthly charges amount")

    # Add custom field validators to check categorical inputs
    @field_validator('gender')
    @classmethod
    def validate_gender(cls, v):
        if v not in ['Male', 'Female']:
            raise ValueError("Gender must be 'Male' or 'Female'")
        return v

    @field_validator('SeniorCitizen')
    @classmethod
    def validate_senior(cls, v):
        if v not in [0, 1]:
            raise ValueError("SeniorCitizen must be 0 or 1")
        return v

    @field_validator('Partner', 'Dependents', 'PhoneService', 'PaperlessBilling')
    @classmethod
    def validate_yes_no(cls, v, info):
        if v not in ['Yes', 'No']:
            raise ValueError(f"{info.field_name} must be 'Yes' or 'No'")
        return v

    @field_validator('MultipleLines')
    @classmethod
    def validate_multiple_lines(cls, v):
        if v not in ['Yes', 'No', 'No phone service']:
            raise ValueError("MultipleLines must be 'Yes', 'No', or 'No phone service'")
        return v

    @field_validator('InternetService')
    @classmethod
    def validate_internet_service(cls, v):
        if v not in ['DSL', 'Fiber optic', 'No']:
            raise ValueError("InternetService must be 'DSL', 'Fiber optic', or 'No'")
        return v

    @field_validator('OnlineSecurity', 'OnlineBackup', 'DeviceProtection', 'TechSupport', 'StreamingTV', 'StreamingMovies')
    @classmethod
    def validate_internet_subservices(cls, v, info):
        if v not in ['Yes', 'No', 'No internet service']:
            raise ValueError(f"{info.field_name} must be 'Yes', 'No', or 'No internet service'")
        return v

    @field_validator('Contract')
    @classmethod
    def validate_contract(cls, v):
        if v not in ['Month-to-month', 'One year', 'Two year']:
            raise ValueError("Contract must be 'Month-to-month', 'One year', or 'Two year'")
        return v

    @field_validator('PaymentMethod')
    @classmethod
    def validate_payment_method(cls, v):
        valid_methods = [
            'Electronic check', 
            'Mailed check', 
            'Bank transfer (automatic)', 
            'Credit card (automatic)'
        ]
        if v not in valid_methods:
            raise ValueError(f"PaymentMethod must be one of {valid_methods}")
        return v


class PredictionResponse(BaseModel):
    customer_id: str
    probability: float
    prediction: str
    risk_level: str
    engineered_features: Dict[str, Any]
    business_recommendations: list[str]
    timestamp: str


class PredictionHistoryRecord(BaseModel):
    id: int
    customer_id: str
    probability: float
    prediction: str
    risk_level: str
    timestamp: str
    inputs: Dict[str, Any]
