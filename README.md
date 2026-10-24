
# 🚀 PulseIQ — Sales Intelligence Platform

**[🌐 Try the Live Demo](https://pulseiq-sales-bi-assistant-ey9pytasplgrjmvewsyhhw.streamlit.app)**

**[💻 GitHub Repository](https://github.com/pvaishnavi02/PulseIQ-Sales-BI-Assistant)**

**[📚 Backend API Documentation](https://pulseiq-backend-pb05.onrender.com/docs)**

---

# Mini AI Business Intelligence Assistant

A lightweight business intelligence application that answers natural-language questions about sales transactions. It combines a FastAPI backend, SQLite database, deterministic analytics, and an optional Groq-powered AI question classifier with a Streamlit dashboard.

## Features

- Ask questions about total revenue, top-performing products, regional performance, monthly revenue trends, and comparisons between months.
- Classify supported natural-language questions using the Groq API.
- Execute predefined, parameterized SQL analytics rather than allowing the AI to generate SQL.
- Display key metrics, supporting data, and monthly revenue visualizations.
- Validate questions and handle unsupported queries.
- Import and validate sales records from an Excel workbook.
- Run automated tests for analytics and input validation.

## Technology Stack

- **Frontend:** Streamlit
- **Backend API:** FastAPI, Uvicorn
- **Database:** SQLite
- **Data processing:** Python, Pandas
- **AI integration:** Groq API
- **Testing:** Pytest
- **Data import:** OpenPyXL

## Project Structure

```text
sales-bi-assistant/
├── backend/
│   ├── __init__.py
│   ├── analytics.py
│   ├── database.py
│   ├── interpreter.py
│   └── main.py
├── data/
│   └── sales.xlsx
├── tests/
│   └── test_analytics.py
├── app.py
├── requirements.txt
├── .env                 # Create locally; do not commit
├── .gitignore
└── README.md
```

The SQLite database is generated locally from the supplied Excel workbook.

## Setup

### 1. Create and activate a virtual environment

On Windows PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

### 2. Install dependencies

```powershell
python -m pip install -r requirements.txt
```

### 3. Configure the Groq API key

Create a `.env` file in the project root:

```text
GROQ_API_KEY=your_groq_api_key_here
```

Replace the placeholder with your own API key. Never commit `.env` or share the key publicly.

The Groq classifier uses `openai/gpt-oss-120b`. If AI classification is unavailable, the application may fall back to its deterministic question-matching logic for supported questions.

### 4. Build the database

From the project root, run:

```powershell
python -m backend.database
```

This imports the workbook into the local SQLite database. Check the terminal output for imported, rejected, duplicate, or uncalculable records.

## Run the Application

Open two VS Code terminals with the virtual environment activated.

**Terminal 1 — Start the API:**

```powershell
python -m uvicorn backend.main:app --reload
```

API documentation: http://127.0.0.1:8000/docs

Health endpoint: http://127.0.0.1:8000/health

**Terminal 2 — Start the dashboard:**

```powershell
python -m streamlit run app.py
```

Open the local Streamlit URL printed in the terminal, usually http://localhost:8501.

## Example Questions

- What is the total revenue?
- Which product performed best?
- Which region generated the highest revenue?
- Show the monthly revenue trend.
- Compare revenue between January and February 2026.

Supported questions depend on the implemented analytics and validation rules.

## Analytics and Data Handling

The current dataset contains 51 transaction records. The analytics results reported during development were:

- Total net revenue: **1,439,200**
- Completed transactions: **50**
- Completed transactions without calculable revenue: **1**

Revenue calculations exclude returned transactions and records for which revenue cannot be calculated because required data is missing. These rules should be considered when interpreting the results.

## Tests

Run the automated test suite from the project root:

```powershell
python -m pytest tests -v
```

The current analytics test suite contains nine tests covering revenue totals, product and region results, monthly data, month comparisons, and invalid inputs.

## Architecture

1. The user enters a question in the Streamlit interface.
2. Streamlit sends the question to the FastAPI `/ask` endpoint.
3. The interpreter identifies the requested analytics operation using supported rules and AI classification where available.
4. The analytics layer executes predefined SQL queries against SQLite.
5. The API returns structured results, which the dashboard displays as answers, metrics, tables, or charts.

## Limitations and Future Improvements

- Natural-language interpretation is limited to the supported analytics operations.
- AI classification depends on network access and a valid Groq API key.
- The current dataset is small and may not represent all business scenarios.
- Future improvements could include additional filters, richer visualizations, more robust data validation, broader question coverage, and deployment.
