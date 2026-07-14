# Technical Architecture & Database Schema

## 1. Tech Stack
* Frontend & UI Routing: Streamlit (Python)
* Financial Logic & Math: Pandas, NumPy
* Database: PostgreSQL
* Database ORM/Connector: SQLAlchemy or psycopg2

## 2. Database Schema (PostgreSQL)

Table: `historical_transactions`
* `id` (Primary Key, UUID or Auto-increment Integer)
* `transaction_date` (Date)
* `description` (Varchar)
* `amount` (Numeric/Decimal) - Positive for revenue/funding, negative for expenses.
* `category` (Varchar) - e.g., 'Payroll', 'Software', 'Revenue', 'Marketing'.
* `created_at` (Timestamp)

Table: `system_config` (Optional, for storing the current active cash balance if not derived purely from transactions)
* `key` (Varchar)
* `value` (Numeric/Decimal)
* `updated_at` (Timestamp)

## 3. System Flow
1. User uploads a CSV of real banking/accounting data via Streamlit.
2. Pandas reads the CSV, maps columns to the `historical_transactions` schema, and inserts records into PostgreSQL.
3. The backend calculates the 3-month trailing average burn rate and current cash position from PostgreSQL.
4. The Scenario Engine (NumPy/Pandas) takes the baseline cash, baseline burn, and Streamlit slider inputs to project a 24-month future array.
5. Streamlit renders the array as a time-series chart.