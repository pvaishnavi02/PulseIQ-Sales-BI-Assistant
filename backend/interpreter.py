
import json
import os
import re

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
                        "Return JSON only, with keys 'type' and 'months'. "
                        "Allowed types: total_revenue, top_product, "
                        "monthly_revenue, top_region, compare_months, "
                        "unsupported. 'months' must be a list containing "
                        "two YYYY-MM strings for compare_months, otherwise "
                        "an empty list. Only classify questions answerable "
                        "from sales revenue, products, regions, and months. "
                        "Never generate SQL or invent data."
                    ),
                },
                {"role": "user", "content": question},
            ],
            temperature=0,
            max_tokens=100,
            response_format={"type": "json_object"},
        )

        content = response.choices[0].message.content
        result = json.loads(content)

        question_type = result.get("type")
        months = result.get("months", [])

        if question_type not in SUPPORTED_TYPES:
            return None

        if question_type == "compare_months":
            if not isinstance(months, list) or len(months) != 2:
                return None

            for month in months:
                if not isinstance(month, str) or not re.fullmatch(
                    r"20\d{2}-(0[1-9]|1[0-2])", month
                ):
                    return None

        return {"type": question_type, "months": months}

    except Exception as exc:
        # Do not expose API keys, provider responses, or internal errors.
        print(f"AI classification unavailable: {type(exc).__name__}")
        return None


def interpret_question(question):
    """Use deterministic matching first and AI classification as fallback."""
    if not isinstance(question, str) or not question.strip():
        raise ValueError("Please enter a non-empty question.")

    text = question.lower().strip()

    months = re.findall(r"\b(20\d{2}-(?:0[1-9]|1[0-2]))\b", text)

    if any(word in text for word in [
        "compare", "change", "difference", "increased", "decreased"
    ]):
        if len(months) == 2:
            return compare_months(months[0], months[1])

        if len(months) > 2:
            raise ValueError("Please specify exactly two months.")

        ai_result = classify_with_ai(question)
        if ai_result and ai_result["type"] == "compare_months":
            return compare_months(*ai_result["months"])

        raise ValueError(
            "Please specify two months in YYYY-MM format, "
            "for example: Compare revenue between 2026-01 and 2026-02."
        )

    if any(phrase in text for phrase in [
        "monthly trend", "monthly revenue", "revenue by month",
        "month-wise revenue", "revenue trend"
    ]):
        return get_monthly_revenue()

    if any(phrase in text for phrase in [
        "total revenue", "overall revenue", "total sales value",
        "overall sales value"
    ]):
        return get_total_revenue()

    if any(phrase in text for phrase in [
        "top product", "highest revenue product", "product generated",
        "best-selling product", "best performing product",
        "highest sales product"
    ]):
        return get_top_product()

    if any(phrase in text for phrase in [
        "top region", "highest sales region", "highest revenue region",
        "region generated", "best region", "region with highest sales"
    ]):
        return get_top_region()

    # AI is a constrained fallback for questions with unfamiliar wording.
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
