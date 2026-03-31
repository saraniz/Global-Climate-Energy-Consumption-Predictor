import numpy as np
import pandas as pd

DATA_PATH = '../data/cleaned_owiddata.csv'

def load_data():
    df = pd.read_csv("../data/owiddata.csv")

    print(df.head)
    print(df.shape)
    print(df.columns)
    
    return df

def clean_data(df):

    df = df.copy()

    print("Null values before filling:")
    print(df.isnull().sum())

    # select important columns only
    df = df[[
        "country",
        "year",
        "population",
        "gdp",
        "primary_energy_consumption",
        "co2",
        "temperature_change_from_co2"
    ]]
    
    # Fill null values with mean for numerical columns
    df.fillna(df.mean(numeric_only=True), inplace=True)
    
    print("\nNull values after filling:")
    print(df.isnull().sum())

    # sort the order by country and year
    df = df.sort_values(["country", "year"])
    
    return df

def feature_engineer(df):
    df = df.copy()

    #create lag features.lag features help to analyze past values
    # here group by create like mini tables based on country[that mean seperate each countries]
    # then take each mini table primary energy column (this is sorted by country and year before)
    # then shift(1) mean moves values down by 1 row. that mean previous raw value got by next raw like that
    df['energy_lag1'] = df.groupby('country')['primary_energy_consumption'].shift(1)
    df['co2_lag1'] = df.groupby('country')['co2'].shift(1)

    df= df.dropna()

    print("feature columns",df.columns)

    return df

def save_data(df):
    df.to_csv(DATA_PATH, index=False)


def main():
    df = load_data()
    df = clean_data(df)
    df = feature_engineer(df)
    save_data(df)

if __name__ == "__main__":
    main()