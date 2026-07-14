import re

import pandas as pd
import pdfplumber

from utils.csv_utils import REQUIRED_COLUMNS, validate_transactions_df

DATE_PATTERN = r"(\d{1,2}/\d{1,2}/\d{4}|\d{4}-\d{1,2}-\d{1,2}|[A-Za-z]{3,9}\.?\s+\d{1,2},?\s+\d{4})"
AMOUNT_PATTERN = r"(\(?-?\$?[\d,]+\.\d{2}\)?)"
LINE_PATTERN = re.compile(rf"^{DATE_PATTERN}\s+(.+?)\s+{AMOUNT_PATTERN}\s*$")


def _normalize_amount(raw_amount: str) -> str:
    negative = raw_amount.startswith("(") and raw_amount.endswith(")")
    cleaned = raw_amount.strip("()").replace("$", "").replace(",", "")
    if negative and not cleaned.startswith("-"):
        cleaned = "-" + cleaned
    return cleaned


def extract_transactions_from_pdf(uploaded_file) -> pd.DataFrame:
    rows = []
    with pdfplumber.open(uploaded_file) as pdf:
        for page in pdf.pages:
            text = page.extract_text() or ""
            for line in text.splitlines():
                match = LINE_PATTERN.match(line.strip())
                if not match:
                    continue
                date_str, description, amount_str = match.groups()
                rows.append(
                    {
                        "Date": date_str,
                        "Description": description.strip(),
                        "Amount": _normalize_amount(amount_str),
                        "Category": "Uncategorized",
                    }
                )
    return pd.DataFrame(rows, columns=REQUIRED_COLUMNS)


def parse_and_validate_pdf(uploaded_file):
    raw = extract_transactions_from_pdf(uploaded_file)
    if raw.empty:
        raise ValueError(
            "No transactions could be extracted from this PDF. This parser only reads "
            "embedded text (not scanned/image statements), and expects lines shaped like "
            "'<date> <description> <amount>'. Try a CSV export instead if this keeps failing."
        )
    return validate_transactions_df(raw)
