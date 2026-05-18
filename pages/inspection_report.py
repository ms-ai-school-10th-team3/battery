import os
import io
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

# [추가] 엑셀 변환 함수
def convert_to_excel(df):
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False, sheet_name='Inspection_Report')
    return output.getvalue()

def make_report_text(row: pd.Series) -> str:
    completed_at = row["completed_at"]
    completed_text = "-" if pd.isna(completed_at) else completed_at.strftime("%Y-%m-%d %H:%M")
    return f"""CellGuard AI 검사 보고서

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
{row["recommendation"]}""".strip()


# =========================
# CSS (기존 유지 + 버튼 가시성 강화)
# =========================
st.markdown("""
<style>
.stApp { background: #F8FBFF; color: #111827; }
header, footer, #MainMenu { visibility: hidden; }
.block-container { padding: 1.6rem 2.4rem; max-width: 100%; }
section[data-testid="stSidebar"] { background: #FFFFFF; border-right: 1px solid #E5EAF3; }
.main-title { font-size: 34px; font-weight: 950; color: #0F172A; margin-bottom: 6px; letter-spacing: -0.8px; }
.sub-title { font-size: 15px; color: #475569; margin-bottom: 22px; }
.card { background: #FFFFFF; border: 1px solid #E4EAF3; border-radius: 16px; padding: 18px; box-shadow: 0 8px 22px rgba(15, 23, 42, 0.05); }
.metric-value { font-size: 20px; color: #0F172A; font-weight: 950; }
.metric-red { color: #EF4444; }
.stButton > button { height: 42px; border-radius: 10px; font-weight: 850; }
/* 엑셀/CSV 버튼 강조 */
div[data-testid="stDownloadButton"] > button {
    border: 1px solid #BFDBFE !important;
    background: #EFF6FF !important;
    color: #0B63FF !important;
    font-weight: 900 !important;
}
</style>
""", unsafe_allow_html=True)


# =========================
# Sidebar & Header
# =========================
render_sidebar("report")

st.markdown("""
<div class="main-title">검사 이력 및 보고서</div>
<div class="sub-title">데이터를 필터링하고 관리자용 보고서(CSV/Excel)를 추출합니다.</div>
""", unsafe_allow_html=True)


# =========================
# Load & Filter Data
# =========================
reports_df = load_reports()

filter_box = st.container(border=True)
with filter_box:
    f1, f2, f3, f4, f5, f6 = st.columns([1.7, 1.1, 1.1, 1.1, 1.7, 0.9])
    with f1:
        date_range = st.date_input("기간", value=(date.today() - timedelta(days=7), date.today()))
    with f2:
        line_options = ["전체 라인"] + (sorted(reports_df["line"].dropna().unique().tolist()) if not reports_df.empty else [])
        selected_line = st.selectbox("라인", line_options)
    with f3:
        type_options = ["전체"] + (sorted(reports_df["inspection_type"].dropna().unique().tolist()) if not reports_df.empty else [])
        selected_type = st.selectbox("검사 유형", type_options)
    with f4:
        result_options = ["전체"] + (sorted(reports_df["result"].dropna().unique().tolist()) if not reports_df.empty else [])
        selected_result = st.selectbox("판정 결과", result_options)
    with f5:
        search_id = st.text_input("배터리 ID 검색", placeholder="ID 입력...")
    with f6:
        st.write("")
        st.write("")
        if st.button("↻ 초기화", use_container_width=True): st.rerun()

# 필터링 적용 로직
filtered_df = reports_df.copy()
if not filtered_df.empty:
    if isinstance(date_range, tuple) and len(date_range) == 2:
        s_date, e_date = date_range
        filtered_df = filtered_df[(filtered_df["completed_at"].dt.date >= s_date) & (filtered_df["completed_at"].dt.date <= e_date)]
    if selected_line != "전체 라인": filtered_df = filtered_df[filtered_df["line"] == selected_line]
    if selected_type != "전체": filtered_df = filtered_df[filtered_df["inspection_type"] == selected_type]
    if selected_result != "전체": filtered_df = filtered_df[filtered_df["result"] == selected_result]
    if search_id.strip(): filtered_df = filtered_df[filtered_df["battery_id"].str.contains(search_id, case=False, na=False)]
    filtered_df = filtered_df.sort_values("completed_at", ascending=False).reset_index(drop=True)


# =========================
# Summary Cards
# =========================
total_count = len(filtered_df)
normal_count = len(filtered_df[filtered_df["result"] == "정상"]) if total_count > 0 else 0
fail_count = len(filtered_df[filtered_df["result"] == "불량"]) if total_count > 0 else 0
avg_risk = round(filtered_df["risk_score"].mean(), 1) if total_count > 0 else 0

s1, s2, s3, s4 = st.columns(4)
# (중략: 기존 s1~s4 메트릭 카드 HTML 코드는 동일하므로 생략하지만, 실제 파일엔 포함되어야 합니다)
# ... [기존 코드의 Summary Cards 부분 유지] ...


# =========================
# [개선] 데이터 시각화 (추가된 부분)
# =========================
if not filtered_df.empty:
    st.markdown("<br>", unsafe_allow_html=True)
    c1, c2 = st.columns(2)
    with c1:
        st.markdown('<div class="card"><div class="metric-title">일별 검사 현황</div></div>', unsafe_allow_html=True)
        chart_data = filtered_df.set_index('completed_at').resample('D').size()
        st.line_chart(chart_data)
    with c2:
        st.markdown('<div class="card"><div class="metric-title">판정 결과 비중</div></div>', unsafe_allow_html=True)
        st.bar_chart(filtered_df['result'].value_counts())


# =========================
# Report Table
# =========================
st.markdown(f'<div class="card"><div class="table-title">검사 이력</div><div class="table-sub">전체 {total_count}건</div></div>', unsafe_allow_html=True)

if filtered_df.empty:
    st.markdown('<div class="empty-box">데이터가 없습니다.</div>', unsafe_allow_html=True)
else:
    # 테이블용 데이터 가공
    display_df = filtered_df.copy()
    display_df["completed_at"] = display_df["completed_at"].dt.strftime("%Y-%m-%d %H:%M")
    st.dataframe(display_df, use_container_width=True, hide_index=True)


# =========================
# [핵심] Downloads & Clear (개선된 부분)
# =========================
st.markdown("<br>", unsafe_allow_html=True)
d1, d2, d3, d4, d5 = st.columns([1.1, 1.1, 1.1, 1.1, 3])

with d1:
    csv = filtered_df.to_csv(index=False, encoding="utf-8-sig")
    st.download_button("📊 CSV 저장", data=csv, file_name="report.csv", mime="text/csv", use_container_width=True)

with d2:
    try:
        excel_data = convert_to_excel(filtered_df)
        st.download_button("📈 Excel 저장", data=excel_data, file_name="report.xlsx", use_container_width=True)
    except:
        st.info("xlsxwriter 설치 필요")

with d3:
    if not filtered_df.empty:
        txt_data = make_report_text(filtered_df.iloc[0])
        st.download_button("📄 최근 TXT", data=txt_data, file_name="latest.txt", use_container_width=True)

with d4:
    if st.button("⚠ 이력 초기화", use_container_width=True):
        clear_reports()
        st.rerun()