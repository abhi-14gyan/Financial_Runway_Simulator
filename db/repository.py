import getpass
from decimal import Decimal

from sqlalchemy import func, select
from sqlalchemy.dialects.postgresql import insert as pg_insert

from db.models import Budget, HistoricalTransaction, Scenario, SystemConfig, UploadAuditLog

STARTING_BALANCE_KEY = "starting_balance_override"


def upsert_transactions(session, valid_df) -> int:
    """Inserts valid rows, skipping any that collide with the composite
    unique constraint. Returns the number of rows actually inserted."""
    if valid_df.empty:
        return 0

    rows = valid_df.to_dict(orient="records")
    stmt = pg_insert(HistoricalTransaction).values(rows)
    stmt = stmt.on_conflict_do_nothing(
        index_elements=["transaction_date", "description", "amount"]
    ).returning(HistoricalTransaction.id)

    result = session.execute(stmt)
    session.commit()
    return len(result.fetchall())


def get_transaction_count(session) -> int:
    return session.execute(
        select(func.count()).select_from(HistoricalTransaction)
    ).scalar_one()


def get_date_range(session):
    return session.execute(
        select(
            func.min(HistoricalTransaction.transaction_date),
            func.max(HistoricalTransaction.transaction_date),
        )
    ).one()


def get_cash_from_transactions(session) -> Decimal:
    total = session.execute(
        select(func.sum(HistoricalTransaction.amount))
    ).scalar_one()
    return total if total is not None else Decimal("0")


def get_monthly_net_aggregates(session, limit_months: int | None = 3):
    """Returns calendar months that actually have transactions, oldest-to-newest,
    as (month_start, revenue_sum, expense_sum). revenue_sum is the sum of positive
    amounts; expense_sum is the sum of negative amounts expressed as a positive
    magnitude. limit_months=None returns every month with data."""
    month = func.date_trunc("month", HistoricalTransaction.transaction_date)
    revenue = func.sum(
        func.greatest(HistoricalTransaction.amount, 0)
    )
    expense = func.sum(
        func.greatest(-HistoricalTransaction.amount, 0)
    )

    query = (
        select(month.label("month_start"), revenue.label("revenue"), expense.label("expense"))
        .group_by(month)
        .order_by(month.desc())
    )
    if limit_months is not None:
        query = query.limit(limit_months)

    rows = list(session.execute(query).all())
    rows.reverse()
    return [
        (row.month_start.date(), row.revenue or Decimal("0"), row.expense or Decimal("0"))
        for row in rows
    ]


def get_category_totals(session):
    rows = session.execute(
        select(HistoricalTransaction.category, func.sum(HistoricalTransaction.amount))
        .group_by(HistoricalTransaction.category)
        .order_by(func.sum(HistoricalTransaction.amount))
    ).all()
    return [(category, total) for category, total in rows]


def get_category_totals_for_month(session, month_start):
    """Category totals restricted to one calendar month (for budget-vs-actual)."""
    month = func.date_trunc("month", HistoricalTransaction.transaction_date)
    rows = session.execute(
        select(HistoricalTransaction.category, func.sum(HistoricalTransaction.amount))
        .where(month == month_start)
        .group_by(HistoricalTransaction.category)
    ).all()
    return [(category, total) for category, total in rows]


def get_all_transactions(session):
    return session.execute(
        select(HistoricalTransaction).order_by(HistoricalTransaction.transaction_date)
    ).scalars().all()


def get_recent_transactions(session, limit: int = 20):
    return session.execute(
        select(HistoricalTransaction)
        .order_by(HistoricalTransaction.transaction_date.desc())
        .limit(limit)
    ).scalars().all()


def get_config_value(session, key: str):
    row = session.get(SystemConfig, key)
    return row.value if row else None


def set_config_value(session, key: str, value: Decimal) -> None:
    row = session.get(SystemConfig, key)
    if row is None:
        row = SystemConfig(key=key, value=value)
        session.add(row)
    else:
        row.value = value
    session.commit()


def clear_config_value(session, key: str) -> None:
    row = session.get(SystemConfig, key)
    if row is not None:
        session.delete(row)
        session.commit()


def save_scenario(session, name: str, params: dict) -> None:
    stmt = pg_insert(Scenario).values(
        name=name,
        starting_cash=params["starting_cash"],
        revenue_growth_pct=params["revenue_growth_pct"],
        num_new_hires=params["num_new_hires"],
        avg_monthly_salary=params["avg_monthly_salary"],
        overhead_increase_pct=params["overhead_increase_pct"],
    )
    stmt = stmt.on_conflict_do_update(
        index_elements=["name"],
        set_={
            "starting_cash": stmt.excluded.starting_cash,
            "revenue_growth_pct": stmt.excluded.revenue_growth_pct,
            "num_new_hires": stmt.excluded.num_new_hires,
            "avg_monthly_salary": stmt.excluded.avg_monthly_salary,
            "overhead_increase_pct": stmt.excluded.overhead_increase_pct,
        },
    )
    session.execute(stmt)
    session.commit()


def get_all_scenarios(session):
    return session.execute(
        select(Scenario).order_by(Scenario.created_at)
    ).scalars().all()


def delete_scenario(session, scenario_id) -> None:
    row = session.get(Scenario, scenario_id)
    if row is not None:
        session.delete(row)
        session.commit()


def save_budget(session, category: str, monthly_budget: Decimal) -> None:
    stmt = pg_insert(Budget).values(category=category, monthly_budget=monthly_budget)
    stmt = stmt.on_conflict_do_update(
        index_elements=["category"],
        set_={"monthly_budget": stmt.excluded.monthly_budget},
    )
    session.execute(stmt)
    session.commit()


def get_all_budgets(session):
    return session.execute(select(Budget).order_by(Budget.category)).scalars().all()


def delete_budget(session, budget_id) -> None:
    row = session.get(Budget, budget_id)
    if row is not None:
        session.delete(row)
        session.commit()


def log_upload(session, filename: str, file_type: str, rows_inserted: int, rows_duplicate: int, rows_rejected: int) -> None:
    entry = UploadAuditLog(
        filename=filename,
        file_type=file_type,
        uploaded_by=getpass.getuser(),
        rows_inserted=rows_inserted,
        rows_duplicate=rows_duplicate,
        rows_rejected=rows_rejected,
    )
    session.add(entry)
    session.commit()


def get_upload_audit_log(session, limit: int = 50):
    return session.execute(
        select(UploadAuditLog).order_by(UploadAuditLog.uploaded_at.desc()).limit(limit)
    ).scalars().all()
