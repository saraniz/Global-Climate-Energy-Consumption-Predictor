import streamlit as st
import requests
import pandas as pd
import os

# Look for an environment variable. If not found, use localhost.
# When using Docker Compose, this will be http://api:8000
API_URL = os.getenv("API_URL", "http://localhost:8000")

st.set_page_config(page_title="Climate Predictor", layout="wide")

st.title("🌍 Global Energy & Climate Predictor")

# Load data for UI components
df = pd.read_csv("data/cleaned_owiddata.csv")
countries = sorted(df["country"].unique())

col1, col2 = st.columns(2)

with col1:
    country = st.selectbox("Select Country", countries)

with col2:
    # Get the latest year from the dataset
    max_year = int(df["year"].max())
    
    # Generate a list of future years (e.g., next 20 years)
    future_years_list = list(range(max_year + 1, max_year + 21))
    
    # Changed from st.slider to st.selectbox
    year = st.selectbox("Select Future Year", future_years_list)

if st.button("Generate Forecast"):
    with st.spinner("Predicting climate data..."):
        try:
            res = requests.post(f"{API_URL}/predict", params={"country": country, "target_year": year})
            data = res.json()

            if "error" in data:
                st.error(data["error"])
            else:
                # Get historical baseline for trend comparison
                latest_hist = df[df["country"] == country].sort_values("year").iloc[-1]
                
                # Display Metrics
                st.divider()
                m1, m2 = st.columns(2)
                
                energy_val = data["energy_prediction"]
                co2_val = data["co2_prediction"]
                
                # Calculate deltas (differences from last known year)
                energy_delta = energy_val - latest_hist['primary_energy_consumption']
                co2_delta = co2_val - latest_hist['co2']
                
                m1.metric(
                    label="Predicted Energy", 
                    value=f"{energy_val:,.2f} TWh", 
                    delta=f"{energy_delta:,.2f} vs {int(latest_hist['year'])}"
                )
                
                m2.metric(
                    label="Predicted CO2", 
                    value=f"{co2_val:,.2f} MtCO₂", 
                    delta=f"{co2_delta:,.2f} vs {int(latest_hist['year'])}",
                    delta_color="inverse" # Red if increasing, Green if decreasing
                )

                # Insight Logic
                st.subheader("Analysis")
                if co2_val > latest_hist['co2']:
                    st.warning(f"⚠️ By {year}, emissions are projected to rise. Mitigation strategies recommended.")
                elif co2_val < latest_hist['co2']:
                    st.success(f"✅ By {year}, emissions show a downward trend compared to {int(latest_hist['year'])}.")
                else:
                    st.info(f"ℹ️ By {year}, emissions are projected to remain stable.")

        except Exception as e:
            st.error(f"Connection Error: Is the FastAPI server running? ({e})")