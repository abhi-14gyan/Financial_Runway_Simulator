from datetime import date

import numpy as np
import pandas as pd
from dateutil.relativedelta import relativedelta


def compute_baseline(monthly_aggregates):
    """monthly_aggregates: list of (month_start, revenue_sum, expense_sum),
    as returned by db.repository.get_monthly_net_aggregates.

    Returns (avg_monthly_revenue, avg_monthly_expenses) as floats, averaged
    over whatever months are present. Returns (0.0, 0.0) if there's no data.
    """
    if not monthly_aggregates:
        return 0.0, 0.0

    revenues = [float(r) for _, r, _ in monthly_aggregates]
    expenses = [float(e) for _, _, e in monthly_aggregates]
    return sum(revenues) / len(revenues), sum(expenses) / len(expenses)


def project_cash_flow(
    start_date: date,
    starting_cash: float,
    avg_monthly_revenue: float,
    avg_monthly_expenses: float,
    revenue_growth_pct: float,
    new_headcount_cost: float,
    overhead_increase_pct: float,
    months: int = 24,
) -> pd.DataFrame:
    """Projects cash balance forward month by month.

    - Revenue compounds monthly at revenue_growth_pct.
    - Expenses step up once by overhead_increase_pct and stay flat.
    - new_headcount_cost is added as a flat monthly expense.
    """
    growth_rate = revenue_growth_pct / 100.0
    overhead_rate = overhead_increase_pct / 100.0

    month_index = np.arange(1, months + 1)
    revenue = avg_monthly_revenue * (1 + growth_rate) ** month_index
    expenses = np.full(months, avg_monthly_expenses * (1 + overhead_rate)) + new_headcount_cost

    net_change = revenue - expenses
    ending_cash = starting_cash + np.cumsum(net_change)

    dates = [start_date + relativedelta(months=i) for i in month_index]

    return pd.DataFrame(
        {
            "date": dates,
            "revenue": revenue,
            "expenses": expenses,
            "ending_cash": ending_cash,
        }
    )


def compute_runway(projection_df: pd.DataFrame) -> dict:
    """Finds the first projected month where ending_cash <= 0."""
    depleted_rows = projection_df[projection_df["ending_cash"] <= 0]

    if depleted_rows.empty:
        return {"depleted": False, "months_to_depletion": None, "depletion_date": None}

    first = depleted_rows.iloc[0]
    months_to_depletion = int(depleted_rows.index[0]) + 1
    return {
        "depleted": True,
        "months_to_depletion": months_to_depletion,
        "depletion_date": first["date"],
    }


def find_breakeven_growth_pct(
    start_date: date,
    starting_cash: float,
    avg_monthly_revenue: float,
    avg_monthly_expenses: float,
    new_headcount_cost: float,
    overhead_increase_pct: float,
    months: int = 24,
    low: float = -20.0,
    high: float = 100.0,
    tolerance: float = 0.1,
):
    """Binary search for the minimum revenue-growth % (within [low, high]) that
    keeps the 24-month projection from ever depleting. Relies on ending cash
    being monotonically increasing in growth_pct when avg_monthly_revenue > 0.

    Returns:
      - a float growth % if a breakeven point exists within [low, high]
      - `low` if the scenario is already breakeven at the minimum growth %
      - None if breakeven isn't achievable within [low, high], or if there's
        no revenue baseline for growth % to act on.
    """
    if avg_monthly_revenue <= 0:
        return None

    def is_depleted(growth_pct):
        df = project_cash_flow(
            start_date,
            starting_cash,
            avg_monthly_revenue,
            avg_monthly_expenses,
            growth_pct,
            new_headcount_cost,
            overhead_increase_pct,
            months,
        )
        return compute_runway(df)["depleted"]

    if not is_depleted(low):
        return low
    if is_depleted(high):
        return None

    while high - low > tolerance:
        mid = (low + high) / 2
        if is_depleted(mid):
            low = mid
        else:
            high = mid

    return round(high, 2)


def sensitivity_analysis(
    start_date: date,
    starting_cash: float,
    avg_monthly_revenue: float,
    avg_monthly_expenses: float,
    current_params: dict,
    months: int = 24,
) -> pd.DataFrame:
    """Varies each lever independently and measures the impact on the 24-month
    ending cash, holding the other two levers at their current values. Returns
    a DataFrame sorted by impact, descending.

    Revenue Growth is capped to -20%/+20% here (narrower than its slider's
    full -20%/100% range) because 100% *monthly* compounding over 24 months
    produces figures in the hundreds of billions, which would swamp the chart
    scale and make the other two levers' bars visually imperceptible even
    though their underlying numbers are real and meaningful."""
    levers = [
        ("Revenue Growth (%)", "revenue_growth_pct", -20.0, 20.0),
        ("New Headcount Cost ($)", "new_headcount_cost", 0.0, 500_000.0),
        ("Fixed Overhead Increase (%)", "overhead_increase_pct", 0.0, 50.0),
    ]

    rows = []
    for label, key, low_value, high_value in levers:
        for value, bound in [(low_value, "low"), (high_value, "high")]:
            params = dict(current_params)
            params[key] = value
            df = project_cash_flow(
                start_date=start_date,
                starting_cash=starting_cash,
                avg_monthly_revenue=avg_monthly_revenue,
                avg_monthly_expenses=avg_monthly_expenses,
                revenue_growth_pct=params["revenue_growth_pct"],
                new_headcount_cost=params["new_headcount_cost"],
                overhead_increase_pct=params["overhead_increase_pct"],
                months=months,
            )
            rows.append(
                {
                    "lever": label,
                    "bound": bound,
                    "value": value,
                    "ending_cash": df.iloc[-1]["ending_cash"],
                }
            )

    result = pd.DataFrame(rows).pivot(index="lever", columns="bound", values="ending_cash")
    result = result.reset_index()
    result["impact"] = (result["high"] - result["low"]).abs()
    return result.sort_values("impact", ascending=False).reset_index(drop=True)


def compute_baseline_std(monthly_aggregates):
    """Real sample standard deviation of monthly revenue/expense from the
    actual historical months. Returns (None, None) with fewer than 2 months,
    since there's no variance to estimate from a single data point."""
    if len(monthly_aggregates) < 2:
        return None, None

    revenues = np.array([float(r) for _, r, _ in monthly_aggregates])
    expenses = np.array([float(e) for _, _, e in monthly_aggregates])
    return float(np.std(revenues, ddof=1)), float(np.std(expenses, ddof=1))


def monte_carlo_projection(
    start_date: date,
    starting_cash: float,
    avg_monthly_revenue: float,
    avg_monthly_expenses: float,
    revenue_std: float,
    expense_std: float,
    revenue_growth_pct: float,
    new_headcount_cost: float,
    overhead_increase_pct: float,
    months: int = 24,
    num_simulations: int = 500,
    seed: int | None = None,
) -> pd.DataFrame:
    """Runs many simulated trajectories with per-month Gaussian noise drawn
    from the real historical std devs, and returns the 10th/50th/90th
    percentile ending cash at each month."""
    rng = np.random.default_rng(seed)
    growth_rate = revenue_growth_pct / 100.0
    overhead_rate = overhead_increase_pct / 100.0

    month_index = np.arange(1, months + 1)
    base_revenue = avg_monthly_revenue * (1 + growth_rate) ** month_index
    base_expenses = np.full(months, avg_monthly_expenses * (1 + overhead_rate)) + new_headcount_cost

    revenue_noise = rng.normal(0, revenue_std, size=(num_simulations, months))
    expense_noise = rng.normal(0, expense_std, size=(num_simulations, months))

    simulated_revenue = np.clip(base_revenue + revenue_noise, 0, None)
    simulated_expenses = np.clip(base_expenses + expense_noise, 0, None)

    ending_cash = starting_cash + np.cumsum(simulated_revenue - simulated_expenses, axis=1)

    dates = [start_date + relativedelta(months=i) for i in month_index]

    return pd.DataFrame(
        {
            "date": dates,
            "p10": np.percentile(ending_cash, 10, axis=0),
            "p50": np.percentile(ending_cash, 50, axis=0),
            "p90": np.percentile(ending_cash, 90, axis=0),
        }
    )
