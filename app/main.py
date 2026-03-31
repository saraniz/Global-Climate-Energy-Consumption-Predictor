from fastapi import FastAPI
import joblib
import pandas as pd
import numpy as np

app = FastAPI()

# Load models and data
energy_model = joblib.load("model/energy_model.pkl")
co2_model = joblib.load("model/co2_model.pkl")
df = pd.read_csv("data/cleaned_owiddata.csv")

# Identify country columns from training
all_cols = pd.get_dummies(df, columns=["country"]).columns
country_cols = [c for c in all_cols if c.startswith("country_")]
base_features = ["year", "population", "gdp", "energy_lag1", "co2_lag1"]
features_order = base_features + country_cols

@app.get('/')
def home():
    return {"status": "running"}

@app.post('/predict')
def predict(country: str, target_year: int):
    # 1. Get the latest historical data for this country
    country_df = df[df["country"] == country].sort_values("year")
    if country_df.empty:
        return {"error": "Country not found"}
    
    latest_record = country_df.iloc[-1]
    current_year = int(latest_record["year"])
    
    # If the user asks for a year already in the past
    if target_year <= current_year:
        return {
            "country": country,
            "year": target_year,
            "energy_prediction": float(latest_record["primary_energy_consumption"]),
            "co2_prediction": float(latest_record["co2"]),
            "note": "Year is in the past or current; returning historical data."
        }

    # 2. Recursive Forecasting Logic
    # We start from the last known state and step forward year by year
    moving_pop = latest_record["population"]
    moving_gdp = latest_record["gdp"]
    moving_energy_lag = latest_record["primary_energy_consumption"]
    moving_co2_lag = latest_record["co2"]

    prediction_energy = 0
    prediction_co2 = 0

    for y in range(current_year + 1, target_year + 1):
        # Estimate growth for Pop and GDP (Simple 1% and 2% annual growth)
        moving_pop *= 1.01 
        moving_gdp *= 1.02

        # Prepare input dictionary
        input_dict = {
            "year": y,
            "population": moving_pop,
            "gdp": moving_gdp,
            "energy_lag1": moving_energy_lag,
            "co2_lag1": moving_co2_lag
        }

        # Set One-Hot Encoding for country
        for col in country_cols:
            input_dict[col] = 1 if col == f"country_{country}" else 0

        # Convert to DataFrame with correct column order
        X = pd.DataFrame([input_dict])[features_order]

        # Predict current step
        prediction_energy = energy_model.predict(X)[0]
        prediction_co2 = co2_model.predict(X)[0]

        # Update lags for the NEXT iteration (Recursive step)
        moving_energy_lag = prediction_energy
        moving_co2_lag = prediction_co2

    return {
        "country": country,
        "year": target_year,
        "energy_prediction": float(prediction_energy),
        "co2_prediction": float(prediction_co2)
    }