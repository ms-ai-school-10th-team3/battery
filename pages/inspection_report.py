import os
from datetime import datetime, date, timedelta

import pandas as pd
import streamlit as st
from components.sidebar import render_sidebar


# =========================
# Page Config
# =========================
st.set_page_config(
    page_title="Inspection Report",
    page_icon="📋",
    layout="wide",
    initial_sidebar_state="expanded",
)

if "login" not in st.session_state or not st.session_state["login"]:
    st.switch_page("streamlit_app.py")


# =========================
# Constants
# =========================
REPORT_DIR = "data"
REPORT_PATH = os.path.join(REPORT_DIR, "reports.csv")

REPORT_COLUMNS = [
    "battery_id",
    "inspection_type",
    "result",
    "risk_score",
    "completed_at",
    "operator",
    "line",
    "confidence",
    "defect_summary",
    "recommendation",
    "model_version",
]

os.makedirs(REPORT_DIR, exist_ok=True)


# =========================
# Data Functions
# =========================
def load_reports() -> pd.DataFrame:
    if not os.path.exists(REPORT_PATH):
        return pd.DataFrame(columns=REPORT_COLUMNS)

    df = pd.read_csv(REPORT_PATH)

    for col in REPORT_COLUMNS:
        if col not in df.columns:
            df[col] = ""

    df = df[REPORT_COLUMNS]
    df["completed_at"] = pd.to_datetime(df["completed_at"], errors="coerce")
    df["risk_score"] = pd.to_numeric(df["risk_score"], errors="coerce").fillna(0).astype(int)
    df["confidence"] = pd.to_numeric(df["confidence"], errors="coerce").fillna(0).astype(int)

    return df


def clear_reports():
    empty_df = pd.DataFrame(columns=REPORT_COLUMNS)
    empty_df.to_csv(REPORT_PATH, index=False, encoding="utf-8-sig")


def make_report_text(row: pd.Series) -> str:
    completed_at = row["completed_at"]

    if pd.isna(completed_at):
        completed_text = "-"
    else:
        completed_text = completed_at.strftime("%Y-%m-%d %H:%M")

    return f"""
CellGuard AI 검사 보고서

배터리 ID: {row["battery_id"]}
검사 유형: {row["inspection_type"]}
판정 결과: {row["result"]}
위험도: {row["risk_score"]}%
신뢰도: {row["confidence"]}%
검사 완료 시간: {completed_text}
작업자: {row["operator"]}
라인: {row["line"]}
모델 버전: {row["model_version"]}

결함 요약:
{row["defect_summary"]}

권장 조치:
{row["recommendation"]}
""".strip()


# =========================
# CSS
# =========================
st.markdown(
    """
<style>
.stApp {
    background: #F8FBFF;
    color: #111827;
}

header, footer, #MainMenu {
    visibility: hidden;
}

.block-container {
    padding-top: 1.6rem;
    padding-left: 2.4rem;
    padding-right: 2.4rem;
    padding-bottom: 2rem;
    max-width: 100%;
}

section[data-testid="stSidebar"] {
    background: #FFFFFF;
    border-right: 1px solid #E5EAF3;
}

.main-title {
    font-size: 34px;
    font-weight: 950;
    color: #0F172A;
    margin-bottom: 6px;
    letter-spacing: -0.8px;
}

.sub-title {
    font-size: 15px;
    color: #475569;
    margin-bottom: 22px;
}

.card {
    background: #FFFFFF;
    border: 1px solid #E4EAF3;
    border-radius: 16px;
    padding: 18px;
    box-shadow: 0 8px 22px rgba(15, 23, 42, 0.05);
}

.metric-title {
    font-size: 15px;
    color: #334155;
    font-weight: 900;
    margin-bottom: 14px;
}

.metric-row {
    display: flex;
    justify-content: space-between;
    align-items: center;
}

.metric-label {
    font-size: 13px;
    color: #64748B;
    font-weight: 800;
}

.metric-value {
    font-size: 20px;
    color: #0F172A;
    font-weight: 950;
}

.metric-red {
    color: #EF4444;
}

.table-title {
    font-size: 20px;
    font-weight: 950;
    color: #0F172A;
    margin-bottom: 4px;
}

.table-sub {
    font-size: 13px;
    color: #64748B;
    font-weight: 700;
    margin-bottom: 14px;
}

.empty-box {
    background: #FFFFFF;
    border: 1px dashed #CBD5E1;
    border-radius: 16px;
    padding: 60px 20px;
    text-align: center;
    color: #64748B;
    font-weight: 800;
}

.stButton > button {
    height: 42px;
    border-radius: 10px;
    border: 1px solid #D7E1F2;
    background: #FFFFFF;
    color: #111827;
    font-weight: 850;
}

.stButton > button:hover {
    border-color: #0B63FF;
    color: #0B63FF;
}

div[data-testid="stDownloadButton"] > button {
    height: 42px;
    border-radius: 10px;
    border: 1px solid #BFDBFE;
    background: #EFF6FF;
    color: #0B63FF;
    font-weight: 900;
}
</style>
""",
    unsafe_allow_html=True,
)


# =========================
# Sidebar
# =========================
render_sidebar("report")


# =========================
# Header
# =========================
st.markdown(
    """
<div class="main-title">검사 이력 및 보고서</div>
<div class="sub-title">외관 검사와 CT 내부검사 결과를 조회하고 저장된 리포트를 확인합니다.</div>
""",
    unsafe_allow_html=True,
)


# =========================
# Load Data
# =========================
reports_df = load_reports()


# =========================
# Filters
# =========================
filter_box = st.container(border=True)

with filter_box:
    f1, f2, f3, f4, f5, f6 = st.columns([1.7, 1.1, 1.1, 1.1, 1.7, 0.9])

    with f1:
        date_range = st.date_input(
            "기간",
            value=(date.today() - timedelta(days=7), date.today()),
        )

    with f2:
        line_options = ["전체 라인"]
        if not reports_df.empty:
            line_options += sorted(reports_df["line"].dropna().astype(str).unique().tolist())

        selected_line = st.selectbox("라인", line_options)

    with f3:
        type_options = ["전체"]
        if not reports_df.empty:
            type_options += sorted(reports_df["inspection_type"].dropna().astype(str).unique().tolist())

        selected_type = st.selectbox("검사 유형", type_options)

    with f4:
        result_options = ["전체"]
        if not reports_df.empty:
            result_options += sorted(reports_df["result"].dropna().astype(str).unique().tolist())

        selected_result = st.selectbox("판정 결과", result_options)

    with f5:
        search_id = st.text_input("배터리 ID 검색", placeholder="배터리 ID 검색")

    with f6:
        st.write("")
        st.write("")
        reset_clicked = st.button("↻ 초기화", use_container_width=True)

if reset_clicked:
    st.rerun()


# =========================
# Apply Filters
# =========================
filtered_df = reports_df.copy()

if not filtered_df.empty:
    if isinstance(date_range, tuple) and len(date_range) == 2:
        start_date, end_date = date_range
        filtered_df = filtered_df[
            (filtered_df["completed_at"].dt.date >= start_date)
            & (filtered_df["completed_at"].dt.date <= end_date)
        ]

    if selected_line != "전체 라인":
        filtered_df = filtered_df[filtered_df["line"] == selected_line]

    if selected_type != "전체":
        filtered_df = filtered_df[filtered_df["inspection_type"] == selected_type]

    if selected_result != "전체":
        filtered_df = filtered_df[filtered_df["result"] == selected_result]

    if search_id.strip():
        filtered_df = filtered_df[
            filtered_df["battery_id"].astype(str).str.contains(search_id.strip(), case=False, na=False)
        ]

    filtered_df = filtered_df.sort_values("completed_at", ascending=False).reset_index(drop=True)


# =========================
# Summary Cards
# =========================
total_count = len(filtered_df)
normal_count = len(filtered_df[filtered_df["result"] == "정상"]) if not filtered_df.empty else 0
fail_count = len(filtered_df[filtered_df["result"] == "불량"]) if not filtered_df.empty else 0
avg_risk = round(filtered_df["risk_score"].mean(), 1) if total_count > 0 else 0

s1, s2, s3, s4 = st.columns(4)

with s1:
    st.markdown(
        f"""
<div class="card">
    <div class="metric-title">전체 보고서</div>
    <div class="metric-row">
        <span class="metric-label">조회 결과</span>
        <span class="metric-value">{total_count}건</span>
    </div>
</div>
""",
        unsafe_allow_html=True,
    )

with s2:
    st.markdown(
        f"""
<div class="card">
    <div class="metric-title">정상</div>
    <div class="metric-row">
        <span class="metric-label">정상 판정</span>
        <span class="metric-value">{normal_count}건</span>
    </div>
</div>
""",
        unsafe_allow_html=True,
    )

with s3:
    st.markdown(
        f"""
<div class="card">
    <div class="metric-title">불량</div>
    <div class="metric-row">
        <span class="metric-label">불량 판정</span>
        <span class="metric-value metric-red">{fail_count}건</span>
    </div>
</div>
""",
        unsafe_allow_html=True,
    )

with s4:
    st.markdown(
        f"""
<div class="card">
    <div class="metric-title">평균 위험도</div>
    <div class="metric-row">
        <span class="metric-label">Risk Score</span>
        <span class="metric-value">{avg_risk}%</span>
    </div>
</div>
""",
        unsafe_allow_html=True,
    )


st.markdown("<br>", unsafe_allow_html=True)


# =========================
# Report Table
# =========================
st.markdown(
    f"""
<div class="card">
    <div class="table-title">검사 이력</div>
    <div class="table-sub">전체 {total_count}건</div>
</div>
""",
    unsafe_allow_html=True,
)

if filtered_df.empty:
    st.markdown(
        """
<div class="empty-box">
    아직 저장된 검사 보고서가 없습니다.<br>
    외관 검사 또는 CT 내부검사 페이지에서 이미지를 업로드하고 AI 분석을 완료하면 이곳에 자동으로 저장됩니다.
</div>
""",
        unsafe_allow_html=True,
    )

    csv_data = pd.DataFrame(columns=REPORT_COLUMNS).to_csv(index=False, encoding="utf-8-sig")

else:
    display_df = filtered_df.copy()

    display_df["검사 완료 시간"] = display_df["completed_at"].dt.strftime("%Y-%m-%d %H:%M")
    display_df["위험도"] = display_df["risk_score"].astype(str) + "%"
    display_df["신뢰도"] = display_df["confidence"].astype(str) + "%"

    display_df = display_df[
        [
            "battery_id",
            "inspection_type",
            "result",
            "위험도",
            "신뢰도",
            "검사 완료 시간",
            "operator",
            "line",
            "model_version",
            "defect_summary",
            "recommendation",
        ]
    ]

    display_df = display_df.rename(
        columns={
            "battery_id": "배터리 ID",
            "inspection_type": "검사 유형",
            "result": "판정 결과",
            "operator": "작업자",
            "line": "라인",
            "model_version": "모델 버전",
            "defect_summary": "결함 요약",
            "recommendation": "권장 조치",
        }
    )

    st.dataframe(
        display_df,
        use_container_width=True,
        hide_index=True,
        column_config={
            "판정 결과": st.column_config.TextColumn("판정 결과"),
            "결함 요약": st.column_config.TextColumn("결함 요약", width="large"),
            "권장 조치": st.column_config.TextColumn("권장 조치", width="large"),
        },
    )

    csv_data = filtered_df.to_csv(index=False, encoding="utf-8-sig")


# =========================
# Downloads / Clear
# =========================
st.markdown("<br>", unsafe_allow_html=True)

d1, d2, d3, d4 = st.columns([1.1, 1.1, 1.1, 4])

with d1:
    st.download_button(
        label="CSV 다운로드",
        data=csv_data,
        file_name=f"cellguard_reports_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
        mime="text/csv",
        use_container_width=True,
    )

with d2:
    if not filtered_df.empty:
        first_report_text = make_report_text(filtered_df.iloc[0])
    else:
        first_report_text = "조회된 보고서가 없습니다."

    st.download_button(
        label="최근 보고서 TXT",
        data=first_report_text,
        file_name="latest_inspection_report.txt",
        mime="text/plain",
        use_container_width=True,
    )

with d3:
    if st.button("보고서 초기화", use_container_width=True):
        clear_reports()
        st.success("보고서 이력이 초기화되었습니다.")
        st.rerun()