import io

import pandas as pd

REQUIRED_COLUMNS = ["Date", "Description", "Amount", "Category"]


def generate_template_csv() -> bytes:
    template = pd.DataFrame(columns=REQUIRED_COLUMNS)
    buffer = io.StringIO()
    template.to_csv(buffer, index=False)
    return buffer.getvalue().encode("utf-8")


def validate_transactions_df(raw_df: pd.DataFrame):
    df = raw_df[REQUIRED_COLUMNS].copy()
    reasons = pd.Series([""] * len(df), index=df.index)

    parsed_date = pd.to_datetime(df["Date"], errors="coerce")
    bad_date = parsed_date.isna()
    reasons.loc[bad_date] += "invalid date; "

    parsed_amount = pd.to_numeric(df["Amount"], errors="coerce")
    bad_amount = parsed_amount.isna()
    reasons.loc[bad_amount] += "invalid amount; "

    bad_description = df["Description"].isna() | (df["Description"].astype(str).str.strip() == "")
    reasons.loc[bad_description] += "missing description; "

    bad_category = df["Category"].isna() | (df["Category"].astype(str).str.strip() == "")
    reasons.loc[bad_category] += "missing category; "

    is_bad = bad_date | bad_amount | bad_description | bad_category

    df["transaction_date"] = parsed_date.dt.date
    df["amount"] = parsed_amount
    df["description"] = df["Description"].astype(str).str.strip()
    df["category"] = df["Category"].astype(str).str.strip()

    valid_df = (
        df.loc[~is_bad, ["transaction_date", "description", "amount", "category"]]
        .reset_index(drop=True)
    )

    rejected_df = raw_df.loc[is_bad].copy()
    rejected_df["reason"] = reasons.loc[is_bad].str.rstrip("; ")

    return valid_df, rejected_df


def parse_and_validate(uploaded_file):
    raw = pd.read_csv(uploaded_file, dtype=str)

    missing = [c for c in REQUIRED_COLUMNS if c not in raw.columns]
    if missing:
        raise ValueError(
            f"CSV is missing required column(s): {', '.join(missing)}. "
            f"Expected exactly: {', '.join(REQUIRED_COLUMNS)}."
        )

    return validate_transactions_df(raw)
