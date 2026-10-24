
from backend.database import get_connection


def query_all(sql, params=()):
    """Execute a read-only analytics query and return dictionaries."""
    with get_connection(read_only=True) as connection:
        return [
            dict(row)
            for row in connection.execute(sql, params).fetchall()
        ]


def get_total_revenue():
    rows = query_all("""
        SELECT
            COALESCE(SUM(revenue), 0) AS total_revenue,
            COUNT(*) AS completed_transactions,
            SUM(CASE WHEN revenue IS NULL THEN 1 ELSE 0 END)
                AS transactions_without_revenue
        FROM sales
        WHERE status = 'Completed'
    """)

    result = rows[0]
    return {
        "question_type": "total_revenue",
        "answer": (
            f"Total net revenue from completed transactions is "
            f"{result['total_revenue']:.2f}."
        ),
        "metrics": result,
        "supporting_data": rows,
    }


def get_top_product():
    rows = query_all("""
        SELECT product, SUM(revenue) AS total_revenue
        FROM sales
        WHERE status = 'Completed' AND revenue IS NOT NULL
        GROUP BY product
        ORDER BY total_revenue DESC, product ASC
    """)

    if not rows:
        return {
            "question_type": "top_product",
            "answer": "No valid completed sales are available.",
            "metrics": {},
            "supporting_data": [],
        }

    top = rows[0]
    return {
        "question_type": "top_product",
        "answer": (
            f"{top['product']} generated the highest recorded revenue "
            f"at {top['total_revenue']:.2f}."
        ),
        "metrics": top,
        "supporting_data": rows,
    }


def get_monthly_revenue():
    rows = query_all("""
        SELECT
            substr(order_date, 1, 7) AS month,
            SUM(revenue) AS total_revenue
        FROM sales
        WHERE status = 'Completed' AND revenue IS NOT NULL
        GROUP BY substr(order_date, 1, 7)
        ORDER BY month
    """)

    return {
        "question_type": "monthly_revenue",
        "answer": f"Monthly revenue is available for {len(rows)} months.",
        "metrics": {"months_reported": len(rows)},
        "supporting_data": rows,
    }


def get_top_region():
    rows = query_all("""
        SELECT region, SUM(revenue) AS total_revenue
        FROM sales
        WHERE status = 'Completed' AND revenue IS NOT NULL
        GROUP BY region
        ORDER BY total_revenue DESC, region ASC
    """)

    if not rows:
        return {
            "question_type": "top_region",
            "answer": "No valid completed sales are available.",
            "metrics": {},
            "supporting_data": [],
        }

    top = rows[0]
    return {
        "question_type": "top_region",
        "answer": (
            f"{top['region']} generated the highest recorded revenue "
            f"at {top['total_revenue']:.2f}."
        ),
        "metrics": top,
        "supporting_data": rows,
    }


def compare_months(month1, month2):
    """Compare months in YYYY-MM format."""
    for month in (month1, month2):
        if (
            not isinstance(month, str)
            or len(month) != 7
            or month[4] != "-"
            or not month[:4].isdigit()
            or not month[5:].isdigit()
            or not 1 <= int(month[5:]) <= 12
        ):
            raise ValueError("Months must use YYYY-MM format.")

    rows = query_all("""
        SELECT
            substr(order_date, 1, 7) AS month,
            SUM(revenue) AS total_revenue
        FROM sales
        WHERE status = 'Completed'
          AND revenue IS NOT NULL
          AND substr(order_date, 1, 7) IN (?, ?)
        GROUP BY substr(order_date, 1, 7)
    """, (month1, month2))

    revenue_by_month = {
        row["month"]: row["total_revenue"]
        for row in rows
    }

    revenue1 = revenue_by_month.get(month1, 0) or 0
    revenue2 = revenue_by_month.get(month2, 0) or 0
    change = revenue2 - revenue1

    percentage_change = (
        (change / revenue1 * 100)
        if revenue1 != 0 else None
    )

    return {
        "question_type": "compare_months",
        "answer": (
            f"Revenue changed by {change:.2f} from {month1} "
            f"to {month2}."
        ),
        "metrics": {
            "month1": month1,
            "revenue1": revenue1,
            "month2": month2,
            "revenue2": revenue2,
            "absolute_change": change,
            "percentage_change": percentage_change,
        },
        "supporting_data": [
            {"month": month1, "total_revenue": revenue1},
            {"month": month2, "total_revenue": revenue2},
        ],
    }
