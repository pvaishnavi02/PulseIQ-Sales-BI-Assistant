
import requests
import pandas as pd
import streamlit as st

API_URL = "http://127.0.0.1:8000"

st.set_page_config(
    page_title="Sales BI Assistant",
    page_icon="📊",
    layout="wide",
)

st.title("📊 Sales BI Assistant")
st.caption(
    "Ask business questions and get answers supported by actual sales data."
)

st.info(
    "Revenue includes completed transactions with calculable revenue. "
    "Returned transactions are excluded, and one transaction with a "
    "missing unit price cannot be included in the revenue total."
)

examples = [
    "What is the total revenue?",
    "Which product generated the highest revenue?",
    "What is the monthly revenue trend?",
    "Which region generated the highest sales?",
    "Compare revenue between 2026-01 and 2026-02",
]

st.subheader("Ask a question")

selected = st.selectbox(
    "Try an example",
    ["Choose a question..."] + examples,
)

with st.form("question_form"):
    question = st.text_input(
        "Your question",
        value="" if selected == "Choose a question..." else selected,
        placeholder="e.g. What is the total revenue?",
    )
    submitted = st.form_submit_button("Analyze", type="primary")

if submitted:
    if not question.strip():
        st.warning("Please enter a question.")
    else:
        try:
            with st.spinner("Analyzing your sales data..."):
                response = requests.post(
                    f"{API_URL}/ask",
                    json={"question": question.strip()},
                    timeout=15,
                )

            if response.status_code == 200:
                result = response.json()

                st.subheader("Answer")
                st.success(result.get("answer", "Analysis completed."))

                metrics = result.get("metrics", {})
                if metrics:
                    st.subheader("Key figures")
                    columns = st.columns(min(len(metrics), 4))

                    for index, (name, value) in enumerate(metrics.items()):
                        if value is None:
                            display_value = "Undefined"
                        elif isinstance(value, (int, float)):
                            if "percentage" in name:
                                display_value = f"{value:.2f}%"
                            elif "revenue" in name or "change" in name:
                                display_value = f"{value:,.2f}"
                            else:
                                display_value = f"{value:,}"
                        else:
                            display_value = str(value)

                        columns[index % len(columns)].metric(
                            name.replace("_", " ").title(),
                            display_value,
                        )

                supporting_data = result.get("supporting_data", [])

                if supporting_data:
                    table = pd.DataFrame(supporting_data)

                    st.subheader("Supporting data")
                    st.dataframe(table, use_container_width=True)

                    if (
                        result.get("question_type") == "monthly_revenue"
                        and {"month", "total_revenue"}.issubset(table.columns)
                    ):
                        st.subheader("Monthly revenue trend")
                        st.line_chart(
                            table.set_index("month")[["total_revenue"]]
                        )

            elif response.status_code == 400:
                detail = response.json().get(
                    "detail", "This question is not supported."
                )
                st.warning(detail)

            else:
                st.error(
                    f"Backend returned HTTP {response.status_code}. "
                    "Please try again."
                )

        except requests.RequestException:
            st.error(
                "Cannot connect to the backend. Make sure the FastAPI "
                "server is running in the other terminal."
            )
        except (ValueError, KeyError) as exc:
            st.error(f"Could not process the response: {exc}")

st.divider()
st.caption("Sales BI Assistant | FastAPI | SQLite | Pandas | Streamlit")
