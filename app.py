
import requests
import pandas as pd
import streamlit as st

API_URL = "http://127.0.0.1:8000"

# ---------- Page setup ----------
st.set_page_config(
    page_title="PulseIQ | Sales Intelligence",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ---------- Complete visual theme ----------
st.markdown("""
<style>
    :root {
        --ivory: #f7f1e8;
        --plum: #2b1d2e;
        --muted: #786a7e;
        --coral: #e85d4f;
        --lavender: #e9dff0;
        --white: #fffaf4;
        --border: #e4d6df;
    }

    .stApp {
        background: var(--ivory);
        color: var(--plum);
    }

    [data-testid="stHeader"] {
        background: var(--ivory);
    }

    [data-testid="stAppViewContainer"] {
        background: var(--ivory);
    }

    .block-container {
        max-width: 1180px;
        padding-top: 2rem;
        padding-bottom: 3rem;
    }

    /* Brand header */
    .brand {
        display: flex;
        align-items: center;
        gap: 15px;
        margin: 8px 0 32px;
        overflow: visible;
    }

    .brand-mark {
        flex: 0 0 54px;
        width: 54px;
        height: 54px;
        border-radius: 16px;
        background: var(--coral);
        color: white;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 30px;
        font-weight: 800;
        box-shadow: 0 7px 18px rgba(232, 93, 79, 0.18);
    }

    .brand-name {
        display: block;
        color: var(--plum);
        font-size: 30px;
        font-weight: 800;
        letter-spacing: -0.7px;
        line-height: 1.35;
        padding: 2px 0 4px;
        overflow: visible;
    }

    .brand-sub {
        color: var(--muted);
        font-size: 10px;
        letter-spacing: 2px;
        line-height: 1.5;
    }

    /* Hero */
    .eyebrow {
        color: var(--coral);
        font-size: 11px;
        letter-spacing: 2px;
        font-weight: 800;
        margin-top: 28px;
        margin-bottom: 9px;
    }

    .hero-panel {
        background: var(--plum);
        padding: clamp(25px, 5vw, 52px);
        border-radius: 24px;
        margin: 12px 0 25px;
        position: relative;
        overflow: hidden;
    }

    .hero-kicker {
        color: #f5b7a9;
        font-size: 11px;
        letter-spacing: 2px;
        font-weight: 700;
        margin-bottom: 15px;
    }

    .hero-title {
        color: #fffaf4;
        font-size: clamp(34px, 5vw, 56px);
        font-weight: 800;
        letter-spacing: -2px;
        line-height: 1.1;
        margin: 0 0 15px;
    }

    .hero-title span {
        color: #ff9b8c;
    }

    .hero-copy {
        color: #e0d4e2;
        font-size: 16px;
        line-height: 1.8;
        max-width: 650px;
        margin: 0;
    }

    .hero-chip {
        display: inline-block;
        margin-top: 24px;
        border: 1px solid #665166;
        border-radius: 30px;
        padding: 8px 13px;
        color: #f6d9d3;
        font-size: 11px;
        letter-spacing: 0.5px;
    }

    /* General text */
    h1, h2, h3 {
        color: var(--plum) !important;
        letter-spacing: -0.5px;
    }

    p, label, .stMarkdown {
        color: var(--plum);
    }

    /* Inputs */
    .stTextInput input {
        background: var(--white) !important;
        color: var(--plum) !important;
        border: 1px solid var(--border) !important;
        border-radius: 12px !important;
        min-height: 48px;
    }

    .stTextInput input:focus {
        border-color: var(--coral) !important;
        box-shadow: 0 0 0 1px var(--coral) !important;
    }

    div[data-baseweb="select"] > div {
        background: var(--white);
        color: var(--plum);
        border-color: var(--border);
        border-radius: 12px;
    }

    /* Buttons */
    .stButton > button,
    .stFormSubmitButton > button {
        background: var(--coral) !important;
        color: white !important;
        border: 1px solid var(--coral) !important;
        border-radius: 12px !important;
        min-height: 46px;
        font-weight: 700 !important;
        transition: 0.2s ease;
    }

    .stButton > button:hover,
    .stFormSubmitButton > button:hover {
        background: #c9443c !important;
        border-color: #c9443c !important;
        color: white !important;
    }

    /* Metrics */
    [data-testid="stMetric"] {
        background: var(--white);
        border: 1px solid var(--border);
        border-radius: 16px;
        padding: 19px;
        box-shadow: 0 4px 15px rgba(43, 29, 46, 0.035);
    }

    [data-testid="stMetricLabel"] {
        color: var(--muted) !important;
    }

    [data-testid="stMetricValue"] {
        color: var(--coral) !important;
        font-weight: 750;
    }

    [data-testid="stMetricDelta"] {
        color: var(--muted) !important;
    }

    /* Result boxes */
    [data-testid="stAlert"] {
        border-radius: 13px;
    }

    /* Data tables */
    [data-testid="stDataFrame"] {
        border: 1px solid var(--border);
        border-radius: 12px;
        overflow: hidden;
    }

    /* Footer */
    hr {
        border-color: var(--border);
        margin-top: 35px;
        margin-bottom: 20px;
    }

    .foot {
        color: var(--muted);
        font-size: 12px;
        line-height: 1.8;
    }

    .foot strong {
        color: var(--plum);
        letter-spacing: 1px;
    }

    /* Mobile */
    @media (max-width: 640px) {
        .block-container {
            padding: 1rem 1rem 2rem;
        }

        .brand-name {
            font-size: 27px;
        }

        .brand-sub {
            font-size: 9px;
            letter-spacing: 1.2px;
        }

        .hero-panel {
            border-radius: 18px;
        }
    }
</style>
""", unsafe_allow_html=True)

# ---------- Branding ----------
st.markdown("""
<div class="brand">
    <div class="brand-mark">↗</div>
    <div>
        <div class="brand-name">PulseIQ</div>
        <div class="brand-sub">SALES INTELLIGENCE PLATFORM</div>
    </div>
</div>

<div class="hero-panel">
    <div class="hero-kicker">YOUR BUSINESS, IN FOCUS</div>
    <div class="hero-title">
        Numbers tell a story.<br>
        <span>Find yours.</span>
    </div>
    <p class="hero-copy">
        Explore your sales data using everyday language.
        Discover revenue patterns, compare performance, and
        uncover business insights backed by actual transactions.
    </p>
    <div class="hero-chip">✦ &nbsp; DATA-DRIVEN DECISIONS</div>
</div>
""", unsafe_allow_html=True)

# ---------- Data note ----------
st.markdown("""
<div style="
    background: #fffaf4;
    border: 1px solid #e4d6df;
    border-left: 4px solid #e85d4f;
    padding: 15px 19px;
    border-radius: 12px;
    color: #65566b;
    font-size: 13px;
    line-height: 1.8;">
    <strong style="color:#e85d4f; letter-spacing:1px;">
        DATA NOTE
    </strong><br>
    Revenue includes completed transactions with calculable revenue.
    Returned transactions are excluded. One completed transaction
    has a missing unit price and is excluded from revenue calculations.
</div>
""", unsafe_allow_html=True)

# ---------- Question form ----------
st.markdown(
    '<div class="eyebrow">01 &nbsp; / &nbsp; ASK YOUR DATA</div>',
    unsafe_allow_html=True,
)
st.subheader("What would you like to discover?")

examples = [
    "What is the total revenue?",
    "Which product generated the highest revenue?",
    "What is the monthly revenue trend?",
    "Which region generated the highest sales?",
    "Compare revenue between 2026-01 and 2026-02",
    "Which area contributed the most to our sales?",
    "Are our sales growing month by month?",
    "What was the revenue in May 2026?",
]

selected = st.selectbox(
    "Choose a starting point",
    ["Choose a question..."] + examples,
)

with st.form("question_form"):
    question = st.text_input(
        "Your question",
        value="" if selected == "Choose a question..." else selected,
        placeholder="e.g. Which area contributed the most to our sales?",
    )

    submitted = st.form_submit_button(
        "Explore my data  →",
        type="primary",
        use_container_width=True,
    )

# ---------- Analysis results ----------
if submitted:
    if not question.strip():
        st.warning("Please enter a question to analyse.")
    else:
        try:
            with st.spinner("Exploring your sales data..."):
                response = requests.post(
                    f"{API_URL}/ask",
                    json={"question": question.strip()},
                    timeout=15,
                )

            if response.status_code == 200:
                result = response.json()

                st.markdown(
                    '<div class="eyebrow">02 &nbsp; / &nbsp; YOUR INSIGHT</div>',
                    unsafe_allow_html=True,
                )
                st.subheader("Here's what the data says")
                st.success(result.get("answer", "Analysis completed."))

                metrics = result.get("metrics", {})

                if metrics:
                    st.markdown(
                        '<div class="eyebrow">KEY FIGURES</div>',
                        unsafe_allow_html=True,
                    )

                    items = list(metrics.items())
                    columns = st.columns(min(len(items), 4))

                    for index, (name, value) in enumerate(items):
                        if value is None:
                            display_value = "N/A"
                        elif isinstance(value, (int, float)):
                            if "percentage" in name:
                                display_value = f"{value:,.2f}%"
                            elif name in ("month", "month1", "month2"):
                                display_value = str(value)
                            elif (
                                "revenue" in name or "change" in name
                            ):
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

                    st.markdown(
                        '<div class="eyebrow">03 &nbsp; / &nbsp; THE EVIDENCE</div>',
                        unsafe_allow_html=True,
                    )
                    st.subheader("Supporting data")

                    if (
                        result.get("question_type") == "monthly_revenue"
                        and {"month", "total_revenue"}.issubset(table.columns)
                    ):
                        chart_data = table[
                            ["month", "total_revenue"]
                        ].copy()

                        chart_data["total_revenue"] = pd.to_numeric(
                            chart_data["total_revenue"],
                            errors="coerce",
                        )
                        chart_data = chart_data.dropna().set_index("month")

                        st.markdown(
                            '<div class="eyebrow">MONTHLY REVENUE TREND</div>',
                            unsafe_allow_html=True,
                        )

                        st.line_chart(
                            chart_data,
                            color="#e85d4f",
                            use_container_width=True,
                        )

                    st.dataframe(
                        table,
                        use_container_width=True,
                        hide_index=True,
                    )

            elif response.status_code == 400:
                detail = response.json().get(
                    "detail",
                    "This question is not supported.",
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

# ---------- Footer ----------
st.divider()

st.markdown("""
<div class="foot">
    <strong>PULSEIQ</strong> &nbsp; · &nbsp; SALES INTELLIGENCE<br>
    Built with FastAPI &nbsp; / &nbsp; SQLite &nbsp; / &nbsp;
    Pandas &nbsp; / &nbsp; Streamlit
</div>
""", unsafe_allow_html=True)
