from datetime import date
from decimal import Decimal

import numpy as np

from analytics.scenario import (
    compute_baseline,
    compute_baseline_std,
    compute_runway,
    find_breakeven_growth_pct,
    monte_carlo_projection,
    project_cash_flow,
    sensitivity_analysis,
)


def test_compute_baseline_empty():
    assert compute_baseline([]) == (0.0, 0.0)


def test_compute_baseline_single_month():
    aggregates = [(date(2026, 3, 1), Decimal("5000.00"), Decimal("2150.00"))]
    assert compute_baseline(aggregates) == (5000.0, 2150.0)


def test_compute_baseline_averages_multiple_months():
    aggregates = [
        (date(2026, 1, 1), Decimal("4000.00"), Decimal("2000.00")),
        (date(2026, 2, 1), Decimal("6000.00"), Decimal("2000.00")),
    ]
    avg_revenue, avg_expenses = compute_baseline(aggregates)
    assert avg_revenue == 5000.0
    assert avg_expenses == 2000.0


def test_project_cash_flow_neutral_sliders_grows_cash():
    df = project_cash_flow(
        start_date=date(2026, 1, 1),
        starting_cash=2850.0,
        avg_monthly_revenue=5000.0,
        avg_monthly_expenses=2150.0,
        revenue_growth_pct=0,
        new_headcount_cost=0,
        overhead_increase_pct=0,
        months=24,
    )
    assert len(df) == 24
    assert df.iloc[0]["ending_cash"] == 5700.0
    assert df.iloc[-1]["ending_cash"] == 2850.0 + 24 * 2850.0


def test_project_cash_flow_revenue_growth_compounds():
    df = project_cash_flow(
        start_date=date(2026, 1, 1),
        starting_cash=0.0,
        avg_monthly_revenue=1000.0,
        avg_monthly_expenses=0.0,
        revenue_growth_pct=10,
        new_headcount_cost=0,
        overhead_increase_pct=0,
        months=3,
    )
    assert df.iloc[0]["revenue"] == 1100.0
    assert round(df.iloc[1]["revenue"], 2) == 1210.0
    assert round(df.iloc[2]["revenue"], 2) == 1331.0


def test_project_cash_flow_headcount_cost_deducted_every_month():
    df = project_cash_flow(
        start_date=date(2026, 1, 1),
        starting_cash=2850.0,
        avg_monthly_revenue=5000.0,
        avg_monthly_expenses=2150.0,
        revenue_growth_pct=0,
        new_headcount_cost=50000,
        overhead_increase_pct=0,
        months=24,
    )
    assert df.iloc[0]["ending_cash"] == -44300.0


def test_compute_runway_not_depleted():
    df = project_cash_flow(
        start_date=date(2026, 1, 1),
        starting_cash=2850.0,
        avg_monthly_revenue=5000.0,
        avg_monthly_expenses=2150.0,
        revenue_growth_pct=0,
        new_headcount_cost=0,
        overhead_increase_pct=0,
        months=24,
    )
    runway = compute_runway(df)
    assert runway == {"depleted": False, "months_to_depletion": None, "depletion_date": None}


def test_compute_runway_depleted_month_one():
    df = project_cash_flow(
        start_date=date(2026, 1, 1),
        starting_cash=2850.0,
        avg_monthly_revenue=5000.0,
        avg_monthly_expenses=2150.0,
        revenue_growth_pct=0,
        new_headcount_cost=50000,
        overhead_increase_pct=0,
        months=24,
    )
    runway = compute_runway(df)
    assert runway["depleted"] is True
    assert runway["months_to_depletion"] == 1
    assert runway["depletion_date"] == date(2026, 2, 1)


def test_breakeven_already_met_returns_low_bound():
    result = find_breakeven_growth_pct(
        start_date=date(2026, 1, 1),
        starting_cash=100000.0,
        avg_monthly_revenue=5000.0,
        avg_monthly_expenses=100.0,
        new_headcount_cost=0,
        overhead_increase_pct=0,
    )
    assert result == -20.0


def test_breakeven_not_achievable_returns_none():
    result = find_breakeven_growth_pct(
        start_date=date(2026, 1, 1),
        starting_cash=0.0,
        avg_monthly_revenue=1.0,
        avg_monthly_expenses=100000.0,
        new_headcount_cost=0,
        overhead_increase_pct=0,
    )
    assert result is None


def test_breakeven_no_revenue_baseline_returns_none():
    result = find_breakeven_growth_pct(
        start_date=date(2026, 1, 1),
        starting_cash=1000.0,
        avg_monthly_revenue=0.0,
        avg_monthly_expenses=500.0,
        new_headcount_cost=0,
        overhead_increase_pct=0,
    )
    assert result is None


def test_breakeven_finds_boundary_growth_rate():
    result = find_breakeven_growth_pct(
        start_date=date(2026, 1, 1),
        starting_cash=2850.0,
        avg_monthly_revenue=5000.0,
        avg_monthly_expenses=2150.0,
        new_headcount_cost=3000,
        overhead_increase_pct=0,
    )
    assert result is not None

    df_at_result = project_cash_flow(
        date(2026, 1, 1), 2850.0, 5000.0, 2150.0, result, 3000, 0, months=24
    )
    assert compute_runway(df_at_result)["depleted"] is False

    df_below_result = project_cash_flow(
        date(2026, 1, 1), 2850.0, 5000.0, 2150.0, result - 1, 3000, 0, months=24
    )
    assert compute_runway(df_below_result)["depleted"] is True


def test_sensitivity_analysis_orders_by_impact_descending():
    result = sensitivity_analysis(
        start_date=date(2026, 1, 1),
        starting_cash=2850.0,
        avg_monthly_revenue=5000.0,
        avg_monthly_expenses=2150.0,
        current_params={
            "revenue_growth_pct": 0,
            "new_headcount_cost": 0,
            "overhead_increase_pct": 0,
        },
    )
    assert list(result.columns[:1]) == ["lever"]
    assert result["impact"].is_monotonic_decreasing
    # Revenue Growth is intentionally capped to +/-20% here (not the slider's
    # full 100% max) so the chart stays visually comparable across levers —
    # see the docstring in sensitivity_analysis for why. At this narrower,
    # more realistic range, Headcount Cost's $0-$500k/month swing dominates.
    assert result.iloc[0]["lever"] == "New Headcount Cost ($)"


def test_compute_baseline_std_insufficient_data():
    assert compute_baseline_std([]) == (None, None)
    assert compute_baseline_std([(date(2026, 1, 1), Decimal("5000"), Decimal("2000"))]) == (None, None)


def test_compute_baseline_std_known_values():
    aggregates = [
        (date(2026, 1, 1), Decimal("4000"), Decimal("2000")),
        (date(2026, 2, 1), Decimal("6000"), Decimal("2000")),
    ]
    revenue_std, expense_std = compute_baseline_std(aggregates)
    assert revenue_std == np.std([4000.0, 6000.0], ddof=1)
    assert expense_std == 0.0


def test_monte_carlo_projection_deterministic_with_seed():
    df1 = monte_carlo_projection(
        date(2026, 1, 1), 2850.0, 5000.0, 2150.0, 500.0, 200.0, 0, 0, 0, months=6, num_simulations=100, seed=42
    )
    df2 = monte_carlo_projection(
        date(2026, 1, 1), 2850.0, 5000.0, 2150.0, 500.0, 200.0, 0, 0, 0, months=6, num_simulations=100, seed=42
    )
    assert df1.equals(df2)


def test_monte_carlo_projection_matches_deterministic_when_std_is_zero():
    deterministic_df = project_cash_flow(
        date(2026, 1, 1), 2850.0, 5000.0, 2150.0, 0, 0, 0, months=6
    )
    mc_df = monte_carlo_projection(
        date(2026, 1, 1), 2850.0, 5000.0, 2150.0, 0.0, 0.0, 0, 0, 0, months=6, num_simulations=50, seed=1
    )
    assert list(mc_df["p50"]) == list(deterministic_df["ending_cash"])
    assert list(mc_df["p10"]) == list(deterministic_df["ending_cash"])
    assert list(mc_df["p90"]) == list(deterministic_df["ending_cash"])
