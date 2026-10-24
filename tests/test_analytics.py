
import pytest

from backend.analytics import (
    get_total_revenue,
    get_top_product,
    get_monthly_revenue,
    get_top_region,
    compare_months,
)
from backend.interpreter import interpret_question


# -------------------------
# Total revenue tests
# -------------------------

def test_total_revenue_is_positive():
    result = get_total_revenue()
    assert result["metrics"]["total_revenue"] > 0
    assert result["metrics"]["completed_transactions"] == 50


def test_total_revenue_returns_expected_dataset_value():
    result = get_total_revenue()
    assert result["metrics"]["total_revenue"] == pytest.approx(1439200.0)


def test_total_revenue_reports_uncalculable_transaction():
    result = get_total_revenue()
    assert result["metrics"]["transactions_without_revenue"] == 1


def test_total_revenue_has_supporting_data():
    result = get_total_revenue()
    assert len(result["supporting_data"]) > 0


# -------------------------
# Top product tests
# -------------------------

def test_top_product_returns_supporting_data():
    result = get_top_product()
    assert result["question_type"] == "top_product"
    assert result["metrics"]["product"]
    assert result["metrics"]["total_revenue"] > 0
    assert len(result["supporting_data"]) > 0


def test_top_product_has_valid_answer():
    result = get_top_product()
    assert isinstance(result["answer"], str)
    assert result["answer"].strip()


def test_top_product_revenue_is_positive():
    result = get_top_product()
    assert result["metrics"]["total_revenue"] > 0


# -------------------------
# Monthly revenue tests
# -------------------------

def test_monthly_revenue_has_six_months():
    result = get_monthly_revenue()
    assert result["metrics"]["months_reported"] == 6
    assert len(result["supporting_data"]) == 6


def test_monthly_revenue_contains_expected_months():
    result = get_monthly_revenue()
    months = [
        row["month"]
        for row in result["supporting_data"]
    ]
    assert months == [
        "2026-01",
        "2026-02",
        "2026-03",
        "2026-04",
        "2026-05",
        "2026-06",
    ]


def test_monthly_revenue_values_are_non_negative():
    result = get_monthly_revenue()
    for row in result["supporting_data"]:
        assert row["total_revenue"] >= 0


def test_monthly_revenue_may_be_checked_for_expected_values():
    result = get_monthly_revenue()
    revenue_by_month = {
        row["month"]: row["total_revenue"]
        for row in result["supporting_data"]
    }

    assert revenue_by_month["2026-01"] == 210250
    assert revenue_by_month["2026-02"] == 234600
    assert revenue_by_month["2026-05"] == 318500


# -------------------------
# Top region tests
# -------------------------

def test_top_region_is_south():
    result = get_top_region()
    assert result["metrics"]["region"] == "South"
    assert result["metrics"]["total_revenue"] == 411200


def test_top_region_has_valid_answer():
    result = get_top_region()
    assert isinstance(result["answer"], str)
    assert result["answer"].strip()


def test_top_region_revenue_is_positive():
    result = get_top_region()
    assert result["metrics"]["total_revenue"] > 0


# -------------------------
# Month comparison tests
# -------------------------

def test_month_comparison():
    result = compare_months("2026-01", "2026-02")
    assert result["metrics"]["revenue1"] == 210250
    assert result["metrics"]["revenue2"] == 234600
    assert result["metrics"]["absolute_change"] == 24350
    assert result["metrics"]["percentage_change"] == pytest.approx(
        11.58145, rel=1e-4
    )


def test_month_comparison_with_zero_baseline():
    result = compare_months("2025-01", "2026-01")
    assert result["metrics"]["revenue1"] == 0
    assert result["metrics"]["percentage_change"] is None


def test_month_comparison_equal_months():
    result = compare_months("2026-01", "2026-01")
    assert result["metrics"]["revenue1"] == result["metrics"]["revenue2"]
    assert result["metrics"]["absolute_change"] == 0
    assert result["metrics"]["percentage_change"] == 0


def test_month_comparison_decrease():
    result = compare_months("2026-05", "2026-06")
    assert result["metrics"]["revenue1"] == 318500
    assert result["metrics"]["revenue2"] == 211250
    assert result["metrics"]["absolute_change"] == -107250


def test_invalid_month_is_rejected():
    with pytest.raises(ValueError):
        compare_months("2026-13", "2026-02")


def test_malformed_month_is_rejected():
    with pytest.raises(ValueError):
        compare_months("January", "2026-02")


# -------------------------
# Interpreter tests
# -------------------------

def test_interpreter_handles_total_revenue_question():
    result = interpret_question("What is the total revenue?")
    assert result["question_type"] == "total_revenue"
    assert result["metrics"]["total_revenue"] == pytest.approx(1439200.0)


def test_interpreter_handles_top_product_question():
    result = interpret_question("Which product performed best?")
    assert result["question_type"] == "top_product"
    assert result["metrics"]["product"]


def test_interpreter_handles_region_question():
    result = interpret_question("Which region generated the highest revenue?")
    assert result["question_type"] == "top_region"
    assert result["metrics"]["region"] == "South"


def test_invalid_question_is_rejected():
    with pytest.raises(ValueError):
        interpret_question("Tell me a joke")


def test_interpreter_rejects_random_unsupported_question():
    with pytest.raises(ValueError):
        interpret_question("Tell me a joke about the weather")


def test_empty_question_is_rejected():
    with pytest.raises(ValueError):
        interpret_question("   ")
