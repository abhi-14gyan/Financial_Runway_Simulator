import os

from google import genai

SYSTEM_INSTRUCTION = (
    "You are a financial analyst for a startup. Given the scenario inputs and a "
    "24-month cash projection, write a concise, exactly 2-sentence executive "
    "summary highlighting the profit/loss risk of this specific scenario. "
    "Be direct and quantify risk where possible, e.g. mention runway in months "
    "if cash depletes."
)


def build_prompt(params: dict, projection_df) -> str:
    projection_rows = [
        f"Month {i + 1} ({row.date.strftime('%b %Y')}): ${row.ending_cash:,.2f}"
        for i, row in enumerate(projection_df.itertuples())
    ]

    return (
        "Scenario inputs:\n"
        f"- Starting cash: ${params['starting_cash']:,.2f}\n"
        f"- Monthly revenue growth: {params['revenue_growth_pct']}%\n"
        f"- New hires: {params['num_new_hires']}\n"
        f"- Average monthly salary per hire: ${params['avg_monthly_salary']:,.2f}\n"
        f"- Total new headcount cost: ${params['new_headcount_cost']:,.2f}/month\n"
        f"- Fixed overhead increase: {params['overhead_increase_pct']}%\n\n"
        "24-month cash projection:\n" + "\n".join(projection_rows)
    )


def generate_executive_report(params: dict, projection_df) -> str:
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        return (
            "AI report unavailable: GEMINI_API_KEY is not set in .env. "
            "Add a key from https://aistudio.google.com/apikey to enable this feature."
        )

    model = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
    prompt = build_prompt(params, projection_df)

    try:
        client = genai.Client(api_key=api_key)
        response = client.models.generate_content(
            model=model,
            contents=prompt,
            config={"system_instruction": SYSTEM_INSTRUCTION},
        )
        return response.text
    except Exception as e:
        return f"AI report unavailable: {e}"
