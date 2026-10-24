
from pathlib import Path
import sqlite3

import pandas as pd


# Project paths
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
EXCEL_PATH = DATA_DIR / "sales.xlsx"
DB_PATH = DATA_DIR / "sales.db"

REQUIRED_COLUMNS = [
    "Transaction_Id",
    "Order_date",
    "Product",
    "Category",
    "Region",
    "Sales_channel",
    "Quantity",
    "Unit_price",
    "Discount_amount",
    "Status",
]


def get_connection(read_only=False):
    """Open a SQLite connection to the project database."""
    if read_only:
        connection = sqlite3.connect(
            f"{DB_PATH.as_uri()}?mode=ro",
            uri=True,
        )
    else:
        connection = sqlite3.connect(DB_PATH)

    connection.row_factory = sqlite3.Row
    return connection


def initialize_database():
    """Validate the workbook and import usable transactions into SQLite."""
    if not EXCEL_PATH.exists():
        raise FileNotFoundError(
            f"Sales workbook not found: {EXCEL_PATH}"
        )

    df = pd.read_excel(EXCEL_PATH)

    missing_columns = [
        column for column in REQUIRED_COLUMNS
        if column not in df.columns
    ]
    if missing_columns:
        raise ValueError(
            f"Missing required columns: {missing_columns}"
        )

    # Normalize strings and dates.
    df["Transaction_Id"] = df["Transaction_Id"].astype("string").str.strip()
    df["Product"] = df["Product"].astype("string").str.strip()
    df["Category"] = df["Category"].astype("string").str.strip()
    df["Region"] = df["Region"].astype("string").str.strip()
    df["Sales_channel"] = df["Sales_channel"].astype("string").str.strip()
    df["Status"] = df["Status"].astype("string").str.strip().str.title()

    df["Order_date"] = pd.to_datetime(
        df["Order_date"], errors="coerce"
    )

    for column in ["Quantity", "Unit_price", "Discount_amount"]:
        df[column] = pd.to_numeric(df[column], errors="coerce")

    # Exclude records that cannot identify a transaction or be dated.
    valid = (
        df["Transaction_Id"].notna()
        & df["Transaction_Id"].ne("")
        & df["Order_date"].notna()
        & df["Product"].notna()
        & df["Product"].ne("")
        & df["Region"].notna()
        & df["Region"].ne("")
        & df["Status"].notna()
    )
    rejected_rows = int((~valid).sum())
    df = df.loc[valid].copy()

    # Duplicate IDs are ambiguous, so reject all occurrences.
    duplicate_ids = df["Transaction_Id"].duplicated(keep=False)
    duplicate_rows = int(duplicate_ids.sum())
    df = df.loc[~duplicate_ids].copy()

    # Revenue cannot be calculated without valid quantity, price,
    # and discount data. Keep these rows for audit, with NULL revenue.
    df["revenue"] = (
        df["Quantity"] * df["Unit_price"]
        - df["Discount_amount"]
    )

    invalid_amounts = (
        df["Quantity"].isna()
        | df["Unit_price"].isna()
        | df["Discount_amount"].isna()
        | df["Quantity"].lt(0)
        | df["Unit_price"].lt(0)
        | df["Discount_amount"].lt(0)
        | df["revenue"].lt(0)
    )
    df.loc[invalid_amounts, "revenue"] = None

    # Preserve all identified transactions, including returned records.
    # Analytics will explicitly decide which statuses to include.
    df["Order_date"] = df["Order_date"].dt.strftime("%Y-%m-%d")

    output_columns = [
        "Transaction_Id",
        "Order_date",
        "Product",
        "Category",
        "Region",
        "Sales_channel",
        "Quantity",
        "Unit_price",
        "Discount_amount",
        "Status",
        "revenue",
    ]

    with sqlite3.connect(DB_PATH) as connection:
        connection.execute("""
            CREATE TABLE IF NOT EXISTS sales (
                transaction_id TEXT PRIMARY KEY,
                order_date TEXT NOT NULL,
                product TEXT NOT NULL,
                category TEXT,
                region TEXT NOT NULL,
                sales_channel TEXT,
                quantity REAL,
                unit_price REAL,
                discount_amount REAL,
                status TEXT NOT NULL,
                revenue REAL
            )
        """)

        # Rebuild from the source workbook on each initialization,
        # so the database is reproducible from the supplied data.
        connection.execute("DELETE FROM sales")

        df[output_columns].to_sql(
            "sales",
            connection,
            if_exists="append",
            index=False,
        )

        connection.execute("""
            CREATE INDEX IF NOT EXISTS idx_sales_order_date
            ON sales(order_date)
        """)
        connection.execute("""
            CREATE INDEX IF NOT EXISTS idx_sales_product
            ON sales(product)
        """)
        connection.execute("""
            CREATE INDEX IF NOT EXISTS idx_sales_region
            ON sales(region)
        """)

    return {
        "imported_rows": len(df),
        "rejected_rows": rejected_rows,
        "duplicate_rows": duplicate_rows,
        "uncalculable_revenue_rows": int(invalid_amounts.sum()),
        "database_path": str(DB_PATH),
    }


if __name__ == "__main__":
    print(initialize_database())
