import os
import joblib
import pandas as pd

from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, r2_score
from sklearn.linear_model import Ridge # Better for trends than Random Forest

DATA_PATH = "../data/cleaned_owiddata.csv"
MODEL_DIR = "../model"

os.makedirs(MODEL_DIR, exist_ok=True)


def load_data():
    return pd.read_csv(DATA_PATH)


def prepare_data(df):

    df = df.copy()

    # one-hot encoding for country
    df = pd.get_dummies(df, columns=["country"])

    base_features = [
        "year",
        "population",
        "gdp",
        "energy_lag1",
        "co2_lag1"
    ]

    country_features = [c for c in df.columns if c.startswith("country_")]

    features = base_features + country_features

    X = df[features]

    y_energy = df["primary_energy_consumption"]
    y_co2 = df["co2"]

    return X, y_energy, y_co2, features


def train():

    df = load_data()
    X, y_energy, y_co2, features = prepare_data(df)

    # due to work with time series data shuffle become false 
    X_train, X_test, y_energy_train, y_energy_test = train_test_split(
        X, y_energy,
        test_size=0.2,
        shuffle=False
    )

    X_ctrain, X_ctest, y_co2_train, y_co2_test = train_test_split(
        X, y_co2,
        test_size=0.2,
        shuffle=False
    )

    energy_model = Ridge() 
    energy_model.fit(X_train, y_energy_train)

    energy_preds = energy_model.predict(X_test)

    print("ENERGY MODEL")
    print("MAE:", mean_absolute_error(y_energy_test, energy_preds))
    print("R2:", r2_score(y_energy_test, energy_preds))

    joblib.dump(energy_model, os.path.join(MODEL_DIR, "energy_model.pkl"))


    co2_model = RandomForestRegressor(
        n_estimators=200,
        random_state=42
    )

    co2_model.fit(X_ctrain, y_co2_train)

    co2_preds = co2_model.predict(X_ctest)

    print("CO2 MODEL")
    print("MAE:", mean_absolute_error(y_co2_test, co2_preds))
    print("R2:", r2_score(y_co2_test, co2_preds))

    joblib.dump(co2_model, os.path.join(MODEL_DIR, "co2_model.pkl"))

    print("Training completed successfully")


if __name__ == "__main__":
    train()