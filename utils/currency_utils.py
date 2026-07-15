import requests
import streamlit as st

SUPPORTED_CURRENCIES = ["USD", "EUR", "GBP", "INR", "JPY", "AUD", "CAD"]

CURRENCY_SYMBOLS = {
    "USD": "$",
    "EUR": "€",
    "GBP": "£",
    "INR": "₹",
    "JPY": "¥",
    "AUD": "A$",
    "CAD": "C$",
}


@st.cache_data(ttl=3600)
def get_exchange_rate(target_currency: str) -> float | None:
    """Live USD -> target_currency rate from the Frankfurter API (ECB-sourced,
    no API key required). Returns None on any network/parsing failure so
    callers can fall back to USD rather than show a fabricated rate."""
    if target_currency == "USD":
        return 1.0
    try:
        response = requests.get(
            "https://api.frankfurter.app/latest",
            params={"from": "USD", "to": target_currency},
            timeout=5,
        )
        response.raise_for_status()
        return response.json()["rates"][target_currency]
    except (requests.RequestException, KeyError, ValueError):
        return None
