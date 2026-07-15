from datetime import date
from decimal import Decimal

import altair as alt
import streamlit as st

import pandas as pd

import theme
from analytics.ai_insights import generate_executive_report
from analytics.anomalies import detect_outliers
from analytics.scenario import (
    compute_baseline,
    compute_baseline_std,
    compute_runway,
    find_breakeven_growth_pct,
    monte_carlo_projection,
    project_cash_flow,
    sensitivity_analysis,
)
from db.database import SessionLocal
from db.repository import (
    STARTING_BALANCE_KEY,
    clear_config_value,
    delete_scenario,
    get_all_scenarios,
    get_all_transactions,
    get_cash_from_transactions,
    get_category_totals,
    get_config_value,
    get_date_range,
    get_monthly_net_aggregates,
    get_recent_transactions,
    get_transaction_count,
    get_upload_audit_log,
    log_upload,
    save_scenario,
    set_config_value,
    upsert_transactions,
)
from utils.csv_utils import generate_template_csv, parse_and_validate
from utils.pdf_utils import parse_and_validate_pdf

st.set_page_config(page_title="Financial Runway Simulator", layout="wide")

light_mode = st.sidebar.toggle("Light Theme", key="light_theme", value=False)
theme.set_theme(dark=not light_mode)
theme.inject_custom_css()
theme.register_altair_theme()

session = SessionLocal()

tx_count = get_transaction_count(session)
summed_cash = get_cash_from_transactions(session)
override_value = get_config_value(session, STARTING_BALANCE_KEY)
effective_cash = override_value if override_value is not None else summed_cash

theme.render_hero_header(
    subtitle="Real-time cash runway forecasting, financial planning, and executive "
    "scenario modeling powered by Python.",
    pills=[
        (date.today().strftime("%B %d, %Y"), theme.ACCENT_SECONDARY, "calendar"),
        ("Database Connected", theme.SUCCESS, "check-circle"),
        ("Live" if tx_count > 0 else "No Data Yet", theme.ACCENT if tx_count > 0 else theme.WARNING, "activity"),
    ],
)

# --- Sidebar: Scenario Inputs -------------------------------------------------
st.sidebar.markdown('<div class="sidebar-title">Financial Controls</div>', unsafe_allow_html=True)

with st.sidebar.container(border=True):
    st.markdown("**Starting Cash**")
    scenario_starting_cash = st.number_input(
        "Baseline Starting Cash",
        value=float(effective_cash),
        step=100.0,
        format="%.2f",
        help="Defaults to the Effective Starting Cash from Section 3. Adjusting it here "
        "only affects this what-if scenario, it does not save an override.",
    )

with st.sidebar.container(border=True):
    st.markdown("**Revenue Growth**")
    revenue_growth_pct = st.slider(
        "Monthly Revenue Growth (%)", min_value=-20, max_value=100, value=0
    )

with st.sidebar.container(border=True):
    st.markdown("**Hiring**")
    num_new_hires = st.slider("Number of New Hires", min_value=0, max_value=50, value=0)

with st.sidebar.container(border=True):
    st.markdown("**Salary**")
    avg_monthly_salary = st.number_input(
        "Average Monthly Salary per Hire", value=10_000.0, step=500.0, format="%.2f"
    )

new_headcount_cost = num_new_hires * avg_monthly_salary

with st.sidebar.container(border=True):
    st.markdown("**Overhead**")
    overhead_increase_pct = st.slider(
        "Fixed Overhead Increase (%)", min_value=0, max_value=50, value=0
    )

# --- Section 1: Upload & Ingest ---------------------------------------------
with st.container(border=True, key="upload_section"):
    st.header("1. Upload Historical Transactions")
    uploaded_file = st.file_uploader(
        "Choose a CSV or PDF file  (PDF support reads embedded text only (not OCR) — "
        "use CSV for scanned statements.)",
        type=["csv", "pdf"],
    )

    if uploaded_file is not None:
        try:
            if uploaded_file.name.lower().endswith(".pdf"):
                valid_df, rejected_df = parse_and_validate_pdf(uploaded_file)
            else:
                valid_df, rejected_df = parse_and_validate(uploaded_file)
        except ValueError as e:
            st.error(str(e))
        else:
            st.subheader("Preview")
            st.write(f"{len(valid_df)} valid row(s), {len(rejected_df)} rejected row(s).")
            st.dataframe(valid_df.head(20))

            if not rejected_df.empty:
                with st.expander(f"View {len(rejected_df)} rejected row(s)"):
                    st.dataframe(rejected_df)

            if not valid_df.empty and st.button("Ingest into Database"):
                inserted = upsert_transactions(session, valid_df)
                duplicates = len(valid_df) - inserted
                file_type = "pdf" if uploaded_file.name.lower().endswith(".pdf") else "csv"
                log_upload(
                    session,
                    filename=uploaded_file.name,
                    file_type=file_type,
                    rows_inserted=inserted,
                    rows_duplicate=duplicates,
                    rows_rejected=len(rejected_df),
                )
                st.success(
                    f"Ingestion complete: {inserted} new row(s) inserted, "
                    f"{duplicates} duplicate row(s) skipped."
                )

    exp_col1, exp_col2, exp_col3 = st.columns(3)

    with exp_col1:
        with st.expander("Prefer to use a CSV instead? Download the template"):
            st.write(
                "Format your export exactly as: `Date, Description, Amount, Category`. "
                "Amount should be positive for revenue/funding and negative for expenses."
            )
            st.download_button(
                label="Download CSV Template",
                data=generate_template_csv(),
                file_name="transaction_template.csv",
                mime="text/csv",
            )

    with exp_col2:
        with st.expander("View Upload History (Audit Trail)"):
            audit_log = get_upload_audit_log(session)
            if audit_log:
                st.dataframe(
                    [
                        {
                            "Uploaded At": entry.uploaded_at,
                            "Uploaded By": entry.uploaded_by,
                            "Filename": entry.filename,
                            "Type": entry.file_type,
                            "Inserted": entry.rows_inserted,
                            "Duplicates Skipped": entry.rows_duplicate,
                            "Rejected": entry.rows_rejected,
                        }
                        for entry in audit_log
                    ]
                )
            else:
                st.caption("No uploads recorded yet.")

    with exp_col3:
        with st.expander("Starting Bank Balance Override (Optional)"):
            st.write("Overrides the summed transaction total as your starting cash.")

            current_override = get_config_value(session, STARTING_BALANCE_KEY)
            override_input = st.number_input(
                "Reconciled bank balance",
                value=float(current_override) if current_override is not None else 0.0,
                step=100.0,
                format="%.2f",
            )

            col1, col2 = st.columns(2)
            with col1:
                if st.button("Save Override"):
                    set_config_value(session, STARTING_BALANCE_KEY, Decimal(str(override_input)))
                    st.success("Starting balance override saved.")
            with col2:
                if st.button("Clear Override"):
                    clear_config_value(session, STARTING_BALANCE_KEY)
                    st.success("Override cleared. Will fall back to summed transactions.")

st.divider()

# --- Section 2: Current Data Summary -----------------------------------------
st.header("2. Current Data Summary")

col1, col2, col3 = st.columns(3)
with col1:
    theme.render_kpi_card("Transactions in DB", str(tx_count), icon="database")
with col2:
    theme.render_kpi_card("Sum of All Transactions", f"${summed_cash:,.2f}", icon="wallet")
with col3:
    theme.render_kpi_card(
        "Effective Starting Cash",
        f"${effective_cash:,.2f}",
        icon="trending-up",
        help_text="Manual override if set, otherwise the summed transaction total.",
    )

if tx_count > 0:
    min_date, max_date = get_date_range(session)
    st.write(f"Historical data range: **{min_date}** to **{max_date}**")

    with st.container(border=True, key="recent_tx_card"):
        with st.expander("Most Recent Transactions"):
            recent = get_recent_transactions(session, limit=20)
            st.table(
                [
                    {
                        "Date": t.transaction_date,
                        "Description": t.description,
                        "Amount": float(t.amount),
                        "Category": t.category,
                    }
                    for t in recent
                ]
            )

    category_totals = get_category_totals(session)
    expense_categories = [(cat, float(-total)) for cat, total in category_totals if total < 0]
    if expense_categories:
        st.subheader("Spend by Category")
        spend_df = pd.DataFrame(expense_categories, columns=["Category", "Amount"])
        category_chart = (
            alt.Chart(spend_df)
            .mark_bar()
            .encode(
                x=alt.X("Amount:Q", title="Total Spend ($)"),
                y=alt.Y("Category:N", sort="-x"),
                tooltip=["Category:N", alt.Tooltip("Amount:Q", format=",.2f")],
            )
        )
        st.altair_chart(category_chart, use_container_width=True)

    all_monthly_aggregates = get_monthly_net_aggregates(session, limit_months=None)
    if all_monthly_aggregates:
        with st.container(border=True, key="trend_chart"):
            st.subheader("Monthly Revenue vs. Expense Trend")
            if len(all_monthly_aggregates) == 1:
                st.caption("Only 1 month of data so far — showing a single point. Upload more months to see a real trend line.")
            trend_rows = []
            for month_start, revenue, expense in all_monthly_aggregates:
                trend_rows.append({"Month": month_start, "Type": "Revenue", "Amount": float(revenue)})
                trend_rows.append({"Month": month_start, "Type": "Expense", "Amount": float(expense)})
            trend_df = pd.DataFrame(trend_rows)
            trend_chart = (
                alt.Chart(trend_df)
                .mark_line(point=True)
                .encode(
                    x=alt.X("Month:T"),
                    y=alt.Y("Amount:Q", title="Amount ($)"),
                    color="Type:N",
                    tooltip=["Month:T", "Type:N", alt.Tooltip("Amount:Q", format=",.2f")],
                )
            )
            st.altair_chart(trend_chart, use_container_width=True)
else:
    st.info("No transactions yet. Upload a CSV above to get started.")

st.divider()

# --- Section 3: Key Performance Indicators ------------------------------------
st.header("3. Key Performance Indicators")

if tx_count == 0:
    st.info("Upload historical transactions in Section 1 above to see KPIs.")
else:
    kpi_aggregates = get_monthly_net_aggregates(session, limit_months=3)
    kpi_avg_revenue, kpi_avg_expenses = compute_baseline(kpi_aggregates)

    kpi_col1, kpi_col2, kpi_col3 = st.columns(3)
    if kpi_avg_revenue > 0:
        burn_multiple = kpi_avg_expenses / kpi_avg_revenue
        gross_margin_pct = (kpi_avg_revenue - kpi_avg_expenses) / kpi_avg_revenue * 100
        with kpi_col1:
            theme.render_kpi_card(
                "Burn Multiple",
                f"{burn_multiple:.2f}x",
                icon="scale",
                help_text="Avg monthly expenses ÷ avg monthly revenue (trailing months).",
            )
        with kpi_col2:
            theme.render_kpi_card(
                "Monthly Revenue",
                f"${kpi_avg_revenue:,.2f}",
                icon="trending-up",
                help_text="Average monthly revenue over the trailing months (labeled 'Monthly Revenue,' not 'MRR', since the schema doesn't track recurring vs. one-time revenue).",
            )
        with kpi_col3:
            theme.render_kpi_card(
                "Gross Margin (approx.)",
                f"{gross_margin_pct:.1f}%",
                icon="percent",
                help_text="Uses total expenses as a stand-in for COGS, so treat as approximate.",
            )
    else:
        with kpi_col1:
            theme.render_kpi_card("Burn Multiple", "N/A", icon="scale")
        with kpi_col2:
            theme.render_kpi_card("Monthly Revenue", "N/A", icon="trending-up")
        with kpi_col3:
            theme.render_kpi_card("Gross Margin (approx.)", "N/A", icon="percent")

    breakeven_preview = find_breakeven_growth_pct(
        start_date=date.today(),
        starting_cash=scenario_starting_cash,
        avg_monthly_revenue=kpi_avg_revenue,
        avg_monthly_expenses=kpi_avg_expenses,
        new_headcount_cost=new_headcount_cost,
        overhead_increase_pct=overhead_increase_pct,
    )
    if breakeven_preview is None:
        breakeven_value = "Not achievable"
    elif breakeven_preview == -20.0:
        breakeven_value = "Already breakeven"
    else:
        breakeven_value = f"{breakeven_preview:.1f}%"
    theme.render_kpi_card(
        "Break-Even Growth Rate",
        breakeven_value,
        icon="activity",
        help_text="Minimum Revenue Growth % Needed",
    )

st.divider()

# --- Section 4: Scenario Projection -------------------------------------------
st.header("4. Scenario Projection")

if tx_count == 0:
    st.info("Upload historical transactions in Section 1 above to see a projection.")
else:
    monthly_aggregates = get_monthly_net_aggregates(session, limit_months=3)
    avg_monthly_revenue, avg_monthly_expenses = compute_baseline(monthly_aggregates)

    st.caption(
        f"Baseline computed from the {len(monthly_aggregates)} most recent month(s) "
        f"with data: avg monthly revenue ${avg_monthly_revenue:,.2f}, "
        f"avg monthly expenses ${avg_monthly_expenses:,.2f}."
    )

    projection_df = project_cash_flow(
        start_date=date.today(),
        starting_cash=scenario_starting_cash,
        avg_monthly_revenue=avg_monthly_revenue,
        avg_monthly_expenses=avg_monthly_expenses,
        revenue_growth_pct=revenue_growth_pct,
        new_headcount_cost=new_headcount_cost,
        overhead_increase_pct=overhead_increase_pct,
        months=24,
    )
    runway = compute_runway(projection_df)

    with st.container(border=True, key="hero_chart"):
        st.markdown('<div class="hero-chart-title">Projected Cash Balance</div>', unsafe_allow_html=True)
        st.markdown(
            '<div class="hero-chart-subtitle">24-month forward projection from your real '
            'transaction history and the current scenario sliders.</div>',
            unsafe_allow_html=True,
        )

        if runway["depleted"]:
            theme.render_kpi_card(
                "Runway Depletion Date",
                f"{runway['months_to_depletion']} Months ({runway['depletion_date'].strftime('%b %Y')})",
                icon="activity",
            )
        else:
            theme.render_kpi_card("Runway Depletion Date", "Beyond 24 months", icon="activity")

        chart = (
            alt.Chart(projection_df)
            .mark_line(point=True)
            .encode(
                x=alt.X("date:T", title="Month"),
                y=alt.Y("ending_cash:Q", title="Projected Cash Balance ($)"),
                tooltip=["date:T", alt.Tooltip("ending_cash:Q", format=",.2f")],
            )
            .properties(height=440)
        )
        st.altair_chart(chart, use_container_width=True)

    theme.render_bullet_heading("Executive Report")
    if st.button("Generate AI Executive Report"):
        params = {
            "starting_cash": scenario_starting_cash,
            "revenue_growth_pct": revenue_growth_pct,
            "num_new_hires": num_new_hires,
            "avg_monthly_salary": avg_monthly_salary,
            "new_headcount_cost": new_headcount_cost,
            "overhead_increase_pct": overhead_increase_pct,
        }
        with st.spinner("Generating AI executive report..."):
            report = generate_executive_report(params, projection_df)
        st.info(report)

    theme.render_bullet_heading("Sensitivity Analysis")
    st.caption(
        "Which lever affects your 24-month cash the most? Revenue Growth is capped "
        "to ±20% here for a fair comparison."
    )
    sensitivity_df = sensitivity_analysis(
        start_date=date.today(),
        starting_cash=scenario_starting_cash,
        avg_monthly_revenue=avg_monthly_revenue,
        avg_monthly_expenses=avg_monthly_expenses,
        current_params={
            "revenue_growth_pct": revenue_growth_pct,
            "new_headcount_cost": new_headcount_cost,
            "overhead_increase_pct": overhead_increase_pct,
        },
    )
    tornado_chart = (
        alt.Chart(sensitivity_df)
        .mark_bar()
        .encode(
            x=alt.X("low:Q", title="24-Month Ending Cash ($)"),
            x2="high:Q",
            y=alt.Y(
                "lever:N",
                sort=alt.EncodingSortField(field="impact", order="descending"),
                title=None,
            ),
            tooltip=[
                "lever:N",
                alt.Tooltip("low:Q", format=",.2f"),
                alt.Tooltip("high:Q", format=",.2f"),
            ],
        )
    )
    st.altair_chart(tornado_chart, use_container_width=True)

    with st.container(border=True, key="prob_chart"):
        st.subheader("Probabilistic Projection")
        revenue_std, expense_std = compute_baseline_std(monthly_aggregates)
        if revenue_std is None:
            st.caption("Not enough historical months (need at least 2) to model uncertainty yet.")
        else:
            if len(monthly_aggregates) == 2:
                st.caption(
                    "Based on only 2 months of data — this is a very rough uncertainty "
                    "estimate, not a robust one."
                )
            mc_df = monte_carlo_projection(
                start_date=date.today(),
                starting_cash=scenario_starting_cash,
                avg_monthly_revenue=avg_monthly_revenue,
                avg_monthly_expenses=avg_monthly_expenses,
                revenue_std=revenue_std,
                expense_std=expense_std,
                revenue_growth_pct=revenue_growth_pct,
                new_headcount_cost=new_headcount_cost,
                overhead_increase_pct=overhead_increase_pct,
                months=24,
                num_simulations=500,
                seed=42,
            )
            band = (
                alt.Chart(mc_df)
                .mark_area(opacity=0.3)
                .encode(
                    x=alt.X("date:T", title="Month"),
                    y=alt.Y("p10:Q", title="Projected Cash Balance ($)"),
                    y2="p90:Q",
                )
            )
            median_line = alt.Chart(mc_df).mark_line(color="black").encode(x="date:T", y="p50:Q")
            st.altair_chart(band + median_line, use_container_width=True)

    st.subheader("Save & Compare Scenarios")
    scenario_name = st.text_input("Scenario name")
    if st.button("Save Current Scenario"):
        if scenario_name.strip():
            save_scenario(
                session,
                scenario_name.strip(),
                {
                    "starting_cash": scenario_starting_cash,
                    "revenue_growth_pct": revenue_growth_pct,
                    "num_new_hires": num_new_hires,
                    "avg_monthly_salary": avg_monthly_salary,
                    "overhead_increase_pct": overhead_increase_pct,
                },
            )
            st.success(f"Scenario '{scenario_name.strip()}' saved.")
        else:
            st.error("Enter a name before saving.")

    saved_scenarios = get_all_scenarios(session)
    if saved_scenarios:
        scenario_names = [s.name for s in saved_scenarios]
        selected_names = st.multiselect("Compare saved scenarios", scenario_names)

        if selected_names:
            compare_rows = []
            for s in saved_scenarios:
                if s.name not in selected_names:
                    continue
                s_headcount_cost = float(s.num_new_hires) * float(s.avg_monthly_salary)
                s_df = project_cash_flow(
                    start_date=date.today(),
                    starting_cash=float(s.starting_cash),
                    avg_monthly_revenue=avg_monthly_revenue,
                    avg_monthly_expenses=avg_monthly_expenses,
                    revenue_growth_pct=float(s.revenue_growth_pct),
                    new_headcount_cost=s_headcount_cost,
                    overhead_increase_pct=float(s.overhead_increase_pct),
                    months=24,
                )
                for _, row in s_df.iterrows():
                    compare_rows.append(
                        {"date": row["date"], "ending_cash": row["ending_cash"], "Scenario": s.name}
                    )
            compare_df = pd.DataFrame(compare_rows)
            compare_chart = (
                alt.Chart(compare_df)
                .mark_line(point=True)
                .encode(
                    x=alt.X("date:T", title="Month"),
                    y=alt.Y("ending_cash:Q", title="Projected Cash Balance ($)"),
                    color="Scenario:N",
                    tooltip=[
                        "date:T",
                        "Scenario:N",
                        alt.Tooltip("ending_cash:Q", format=",.2f"),
                    ],
                )
            )
            st.altair_chart(compare_chart, use_container_width=True)

        with st.expander("Delete a saved scenario"):
            delete_name = st.selectbox("Scenario to delete", scenario_names)
            if st.button("Delete Selected Scenario"):
                target = next(s for s in saved_scenarios if s.name == delete_name)
                delete_scenario(session, target.id)
                st.success(f"Deleted '{delete_name}'. Refresh the page to update the list.")
    else:
        st.caption("No saved scenarios yet. Save your current slider settings above to start comparing.")

st.divider()

# --- Section 5: Potential Outliers ---------------------------------------------
st.header("5. Potential Outliers")

if tx_count == 0:
    st.info("Upload historical transactions in Section 1 above to see outlier detection.")
else:
    all_transactions = get_all_transactions(session)
    if len(all_transactions) < 5:
        st.caption("Not enough data yet to detect outliers reliably (need at least 5 transactions).")
    else:
        all_tx_df = pd.DataFrame(
            [
                {
                    "Date": t.transaction_date,
                    "Description": t.description,
                    "amount": float(t.amount),
                    "Category": t.category,
                }
                for t in all_transactions
            ]
        )
        outliers_df = detect_outliers(all_tx_df)
        if outliers_df.empty:
            st.caption("No outliers detected using the IQR method (values outside 1.5x the interquartile range).")
        else:
            st.caption("Flagged using the IQR method (values outside 1.5x the interquartile range) — for review, not automatically excluded.")
            st.dataframe(outliers_df.rename(columns={"amount": "Amount"}))

session.close()
