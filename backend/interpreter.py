
import json
import os
import re
from datetime import datetime

from dotenv import load_dotenv

from backend.analytics import (
    get_total_revenue,
    get_top_product,
    get_monthly_revenue,
    get_top_region,
    compare_months,
)

load_dotenv()

SUPPORTED_TYPES = {
    "total_revenue",
    "top_product",
    "monthly_revenue",
    "top_region",
    "compare_months",
    "unsupported",
}

MONTH_NAMES = {
    "january": "01", "jan": "01",
    "february": "02", "feb": "02",
    "march": "03", "mar": "03",
    "april": "04", "apr": "04",
    "may": "05",
    "june": "06", "jun": "06",
    "july": "07", "jul": "07",
    "august": "08", "aug": "08",
    "september": "09", "sep": "09", "sept": "09",
    "october": "10", "oct": "10",
    "november": "11", "nov": "11",
    "december": "12", "dec": "12",
}


def classify_with_ai(question):
    """Use Groq to classify a question, never to generate SQL."""
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        return None

    try:
        from groq import Groq

        client = Groq(api_key=api_key, timeout=10.0, max_retries=0)
        response = client.chat.completions.create(
            model="openai/gpt-oss-120b",
            messages=[
                {
                    "role": "system",
                    "content": (
                        "Classify the user's sales analytics question. "
                        "Return JSON only with keys 'type' and 'months'. "
                        "Allowed types: total_revenue, top_product, "
                        "monthly_revenue, top_region, compare_months, "
                        "unsupported. For compare_months, months must be "
                        "two YYYY-MM strings. Otherwise use an empty list. "
                        "Only classify questions answerable from sales "
                        "revenue, products, regions, and months. Never "
                        "generate SQL or invent data. If a question asks "
                        "for one month's revenue, classify it as "
                        "monthly_revenue."
                    ),
                },
                {"role": "user", "content": question},
            ],
            temperature=0,
            max_tokens=120,
            response_format={"type": "json_object"},
        )

        result = json.loads(response.choices[0].message.content)
        question_type = result.get("type")
        months = result.get("months", [])

        if question_type not in SUPPORTED_TYPES:
            return None

        if question_type == "compare_months":
            if not isinstance(months, list) or len(months) != 2:
                return None
            if not all(
                isinstance(m, str)
                and re.fullmatch(r"20\d{2}-(0[1-9]|1[0-2])", m)
                for m in months
            ):
                return None
        else:
            months = []

        return {"type": question_type, "months": months}

    except Exception as exc:
        print(f"AI classification unavailable: {type(exc).__name__}")
        return None


def _extract_months(text):
    """Extract YYYY-MM and named month/year references from a question."""
    text = text.lower()
    found = []

    # Match numeric dates such as 2026-01.
    for match in re.finditer(r"\b(20\d{2}-(?:0[1-9]|1[0-2]))\b", text):
        found.append((match.start(), match.group(1)))

    # Match month names, optionally followed by a year.
    pattern = (
        r"\b(january|jan|february|feb|march|mar|april|apr|may|"
        r"june|jun|july|jul|august|aug|september|sept|sep|"
        r"october|oct|november|nov|december|dec)\b"
        r"(?:\s+(?:of\s+)?(20\d{2}))?"
    )

    for match in re.finditer(pattern, text):
        month_name = match.group(1)
        year = match.group(2) or "2026"
        month = f"{year}-{MONTH_NAMES[month_name]}"
        found.append((match.start(), month))

    found.sort(key=lambda item: item[0])

    unique = []
    for _, month in found:
        if month not in unique:
            unique.append(month)

    return unique

def _single_month_result(month):
    """Return the selected month from the monthly analytics result."""
    result = get_monthly_revenue()
    rows = result.get("supporting_data", [])

    for row in rows:
        if row.get("month") == month:
            revenue = row.get("total_revenue")
            return {
                "answer": f"Revenue for {month} is {revenue:,.2f}.",
                "question_type": "monthly_revenue",
                "metrics": {
                    "month": month,
                    "total_revenue": revenue,
                },
                "supporting_data": [row],
            }

    return {
        "answer": f"No revenue data is available for {month}.",
        "question_type": "monthly_revenue",
        "metrics": {"month": month, "total_revenue": 0},
        "supporting_data": [],
    }


def interpret_question(question):
    """Interpret supported sales questions and return analytics results."""
    if not isinstance(question, str) or not question.strip():
        raise ValueError("Please enter a non-empty question.")

    text = question.lower().strip()
    months = _extract_months(text)

    comparison_words = (
    "compare",
    "comparison",
    "change",
    "difference",
    "increased",
    "decreased",
    "versus",
    " vs ",
    "better than",
    "worse than",
    "did ",
    "higher than",
    "lower than",
    "more than",
    "less than",
    )
    is_comparison = any(word in f" {text} " for word in comparison_words)

    
    if is_comparison:
        if len(months) == 2:
            return compare_months(months[0], months[1])

        if len(months) > 2:
            raise ValueError("Please specify exactly two months.")

        ai_result = classify_with_ai(question)
        if ai_result and ai_result["type"] == "compare_months":
            return compare_months(*ai_result["months"])

        # Handle comparisons where month names have no year.
        month_names = re.findall(
            r"\b(january|jan|february|feb|march|mar|april|apr|may|"
            r"june|jun|july|jul|august|aug|september|sept|sep|"
            r"october|oct|november|nov|december|dec)\b",
            text,
        )

        if len(month_names) == 2:
            month1 = f"2026-{MONTH_NAMES[month_names[0]]}"
            month2 = f"2026-{MONTH_NAMES[month_names[1]]}"
            return compare_months(month1, month2)

        raise ValueError(
            "Please specify two months, for example: "
            "Compare revenue between January and February 2026."
        )


    # A specific month question should return just that month's figures.
    if len(months) == 1 and any(
        word in text for word in ("revenue", "sales", "month")
    ):
        return _single_month_result(months[0])

    if any(phrase in text for phrase in (
    "monthly trend",
    "monthly revenue",
    "revenue by month",
    "month-wise revenue",
    "revenue trend",
    "show monthly",
    "sales growing month by month",
    "sales growth month by month",
    "sales trend",
    "month by month",
    "monthly breakdown",
    "month-by-month breakdown",
    "earnings each month",
    "monthly performance",
    )):
        return get_monthly_revenue()

    if any(phrase in text for phrase in (
        "total revenue", "overall revenue", "total sales value",
        "overall sales value", "total sales",
    )):
        return get_total_revenue()

    if any(phrase in text for phrase in (
        "top product", "highest revenue product", "product generated",
        "best-selling product", "best performing product",
        "highest sales product", "which product performed best",
    )):
        return get_top_product()

    if any(phrase in text for phrase in (
        "top region", "highest sales region", "highest revenue region",
        "region generated", "best region", "region with highest sales",
        "which region", "which area of the business",
    )):
        return get_top_region()

    ai_result = classify_with_ai(question)

    if ai_result:
        question_type = ai_result["type"]

        if question_type == "total_revenue":
            return get_total_revenue()
        if question_type == "top_product":
            return get_top_product()
        if question_type == "monthly_revenue":
            return get_monthly_revenue()
        if question_type == "top_region":
            return get_top_region()
        if question_type == "compare_months":
            return compare_months(*ai_result["months"])

    raise ValueError(
        "I couldn't identify a supported sales question. Try asking "
        "about total revenue, the top product, monthly revenue, "
        "the top region, or a comparison between two months."
    )
