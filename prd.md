# Product Requirements Document (PRD): Enterprise Financial Runway Simulator

## 1. Overview
A lightweight, interactive web application designed for startup executives and finance teams to calculate and visualize cash runway depletion based on real historical transaction data and dynamic "what-if" scenario inputs.

## 2. Core Constraints
* STRICT NO-MOCK-DATA POLICY: The system will not contain any scripts that generate synthetic data.
* Data Source: The application must include a Streamlit UI component allowing the user to upload real historical transaction data (CSV format), which the backend will parse, validate, and store in a PostgreSQL database.

## 3. Key Features

### Feature 1: Data Ingestion & Storage
* UI for uploading standard financial export CSVs (Date, Description, Amount, Category).
* Python backend that cleans the data and loads it into a PostgreSQL database.
* Calculation of current cash balance and baseline historical monthly burn rate from the real ingested data.

### Feature 2: Interactive Scenario Engine
* Streamlit sidebar containing input sliders for future projections:
  * Baseline Starting Cash (defaults to the sum of all historical transactions if not explicitly set).
  * Monthly Revenue Growth (%) [Range: -20% to +100%].
  * New Headcount Cost (Monthly) [Range: $0 to $500,000].
  * Fixed Overhead Increase (%) [Range: 0% to 50%].

### Feature 3: Real-Time Visualization
* Dynamic line chart (using Streamlit's native charting or Altair) mapping the projected cash balance over a 24-month forward-looking timeline.
* A prominent "Runway Depletion Date" metric card (e.g., "Cash out in: 14 Months (Oct 2027)").
* Automatic re-calculation and chart re-rendering via Pandas/NumPy when any slider is adjusted.