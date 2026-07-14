import pandas as pd


def detect_outliers(df: pd.DataFrame, min_rows: int = 5) -> pd.DataFrame:
    if len(df) < min_rows:
        return df.iloc[0:0]

    q1 = df["amount"].quantile(0.25)
    q3 = df["amount"].quantile(0.75)
    iqr = q3 - q1
    lower_bound = q1 - 1.5 * iqr
    upper_bound = q3 + 1.5 * iqr

    return df[(df["amount"] < lower_bound) | (df["amount"] > upper_bound)]
