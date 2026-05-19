import os
import io
import textwrap
from datetime import datetime, date, timedelta

import pandas as pd
import streamlit as st


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
# HTML Helper
# =========================
def html(code):
    st.markdown(textwrap.dedent(code).strip(), unsafe_allow_html=True)


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
# 🎨 CSS
# =========================
html("""
<style>
.stApp { background: #F8FBFF; color: #111827; }
header[data-testid="stHeader"] { background-color: rgba(0,0,0,0) !important; }
footer, #MainMenu { visibility: hidden; }
.block-container { padding: 1.6rem 2.4rem; max-width: 100%; }
[data-testid="stSidebar"] { background-color: #FFFFFF !important; border-right: 1px solid #E5EAF3 !important; }
.sidebar-logo-area { margin-bottom: 30px; padding-left: 8px; }
.sidebar-title { font-size: 21px; font-weight: 800; color: #0F172A; display: flex; align-items: center; gap: 10px; }
.sidebar-logo-icon { width: 20px; height: 24px; background: #3B82F6; border-radius: 4px 4px 10px 10px; display: inline-block; }
.sidebar-subtitle { font-size: 12px; font-weight: 600; color: #64748B; margin-top: 4px; padding-left: 30px; }
.operator-card { border: 1px solid #E5EAF3; border-radius: 16px; padding: 16px; background: #FFFFFF; margin-top: 40px; }
.operator-title { font-size: 13.5px; font-weight: 700; color: #475569; margin-bottom: 10px; }
.operator-name { font-size: 16px; font-weight: 800; color: #0F172A; margin-bottom: 16px; padding-left: 22px; }
.operator-time { font-size: 11px; color: #64748B; padding-left: 22px; font-weight: 600; }
div.logout-btn-wrap div.stButton > button { width: 100% !important; height: 42px !important; border: 1px solid #E5EAF3 !important; border-radius: 12px !important; background: #FFFFFF !important; color: #475569 !important; font-weight: 700 !important; font-size: 14px !important; }
.main-title { font-size: 34px; font-weight: 950; color: #0F172A; margin-bottom: 6px; }
.sub-title { font-size: 15px; color: #475469; margin-bottom: 22px; }
.card { background: #FFFFFF; border: 1px solid #E4EAF3; border-radius: 16px; padding: 18px; box-shadow: 0 8px 22px rgba(15, 23, 42, 0.05); margin-bottom: 15px; }
.metric-title { font-size: 13px; font-weight: 700; color: #64748B; margin-bottom: 6px; }
.metric-value { font-size: 26px; color: #0F172A; font-weight: 950; }
.metric-red { color: #EF4444; }
.metric-blue { color: #3B82F6; }
.table-title { font-size: 18px; font-weight: 900; color: #0F172A; }
.table-sub { font-size: 13px; color: #64748B; margin-bottom: 4px; }
.empty-box { background: #FFFFFF; border: 1px dashed #CBD5E1; border-radius: 12px; padding: 40px; text-align: center; color: #64748B; font-weight: 600; }
div[data-testid="stDownloadButton"] > button { border: 1px solid #BFDBFE !important; background: #EFF6FF !important; color: #0B63FF !important; font-weight: 900 !important; height: 42px; border-radius: 10px; }
</style>
""")


# ==================================================
# Sidebar
# ==================================================
with st.sidebar:
    html('<div class="sidebar-logo-area"><div class="sidebar-title"><span class="sidebar-logo-icon"></span> CellGuard AI</div><div class="sidebar-subtitle">Battery Inspection</div></div>')
    st.page_link("pages/exterior_inspection.py", label="🔍 Exterior Inspection", use_container_width=True)
    st.page_link("pages/ct_inspection.py", label="☢ CT Inspection", use_container_width=True)
    st.page_link("pages/inspection_report.py", label="📋 Inspection Report", use_container_width=True)
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M")
    html(f'<div class="operator-card"><div class="operator-title">👤 Operator</div><div class="operator-name">1</div><div class="operator-time">Access Time: {now_str}</div></div>')
    st.markdown('<div class="logout-btn-wrap">', unsafe_allow_html=True)
    if st.button("Logout", key="btn_logout"):
        st.session_state.login = False
        st.switch_page("streamlit_app.py")
    st.markdown('</div>', unsafe_allow_html=True)


# ==================================================
# Main Dashboard
# ==================================================
st.markdown('<div class="main-title">검사 이력 및 보고서</div><div class="sub-title">데이터를 필터링하고 관리자용 보고서(CSV/Excel)를 추출합니다.</div>', unsafe_allow_html=True)

reports_df = load_reports()

# Filter
filter_box = st.container(border=True)
with filter_box:
    f1, f2, f3, f4, f5, f6 = st.columns([1.7, 1.1, 1.1, 1.1, 1.7, 0.9])
    with f1: date_range = st.date_input("기간", value=(date.today() - timedelta(days=7), date.today()))
    with f2: selected_line = st.selectbox("라인", ["전체 라인"] + (sorted(reports_df["line"].dropna().unique().tolist()) if not reports_df.empty else []))
    with f3: selected_type = st.selectbox("검사 유형", ["전체"] + (sorted(reports_df["inspection_type"].dropna().unique().tolist()) if not reports_df.empty else []))
    with f4: selected_result = st.selectbox("판정 결과", ["전체"] + (sorted(reports_df["result"].dropna().unique().tolist()) if not reports_df.empty else []))
    with f5: search_id = st.text_input("배터리 ID 검색", placeholder="ID 입력...")
    with f6:
        st.write("")
        st.write("")
        if st.button("↻ 초기화", use_container_width=True): st.rerun()

# Processing
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

# Metrics
total_count = len(filtered_df)
s1, s2, s3, s4 = st.columns(4)
with s1: st.markdown(f'<div class="card"><div class="metric-title">총 검사 건수</div><div class="metric-value">{total_count}건</div></div>', unsafe_allow_html=True)
with s2: st.markdown(f'<div class="card"><div class="metric-title">정상 판정</div><div class="metric-value metric-blue">{len(filtered_df[filtered_df["result"]=="정상"])}건</div></div>', unsafe_allow_html=True)
with s3: st.markdown(f'<div class="card"><div class="metric-title">결함 탐지(불량)</div><div class="metric-value metric-red">{len(filtered_df[filtered_df["result"]=="불량"])}건</div></div>', unsafe_allow_html=True)
with s4: st.markdown(f'<div class="card"><div class="metric-title">평균 위험도</div><div class="metric-value">{round(filtered_df["risk_score"].mean(), 1) if total_count > 0 else 0}%</div></div>', unsafe_allow_html=True)

# Charts
if not filtered_df.empty:
    c1, c2 = st.columns(2)
    with c1:
        st.markdown('<div class="card"><div class="metric-title">일별 검사 현황</div></div>', unsafe_allow_html=True)
        st.line_chart(filtered_df.set_index('completed_at').resample('D').size(), height=220)
    with c2:
        st.markdown('<div class="card"><div class="metric-title">판정 결과 비중</div></div>', unsafe_allow_html=True)
        st.bar_chart(filtered_df['result'].value_counts(), height=220)


# =========================
# Report Table & Drill-down
# =========================
@st.dialog("📋 상세 검사 리포트")
def show_detail(row):
    st.markdown(f"### 배터리 ID: **{row['battery_id']}**")
    st.divider()
    c1, c2 = st.columns(2)
    with c1:
        st.write(f"**검사 유형:** {row['inspection_type']}")
        st.write(f"**최종 판정:** {row['result']}")
        st.write(f"**위험도:** {row['risk_score']}%")
    with c2:
        st.write(f"**신뢰도:** {row['confidence']}%")
        st.write(f"**라인:** {row['line']}")
        st.write(f"**시간:** {row['completed_at'].strftime('%Y-%m-%d %H:%M')}")
    st.write("---")
    st.markdown("**결함 요약**")
    st.info(row['defect_summary'])
    st.markdown("**권장 조치**")
    st.warning(row['recommendation'])

st.markdown("<br>", unsafe_allow_html=True)
st.markdown(f'<div class="card" style="margin-bottom:8px;"><div class="table-title">상세 검사 이력</div><div class="table-sub">행을 클릭하면 상세 내용을 조회할 수 있습니다. (조회 {total_count}건)</div></div>', unsafe_allow_html=True)

if filtered_df.empty:
    st.markdown('<div class="empty-box">조회된 검사 이력이 없습니다. 필터 조건을 확인하세요.</div>', unsafe_allow_html=True)
else:
    event = st.dataframe(filtered_df, use_container_width=True, hide_index=True, selection_mode="single-row", on_select="rerun")
    if len(event.selection["rows"]) > 0:
        selected_index = event.selection["rows"][0]
        selected_row = filtered_df.iloc[selected_index]
        show_detail(selected_row)


# =========================
# Downloads
# =========================
st.markdown("<br>", unsafe_allow_html=True)
d1, d2, d3, d4, d5 = st.columns([1, 1, 1, 1, 2])
with d1: st.download_button("📊 CSV 내보내기", data=filtered_df.to_csv(index=False, encoding="utf-8-sig"), file_name=f"Report_{date.today()}.csv", use_container_width=True)
with d2:
    try: st.download_button("📈 Excel 내보내기", data=convert_to_excel(filtered_df), file_name=f"Report_{date.today()}.xlsx", use_container_width=True)
    except: st.info("xlsxwriter 필요")
with d3:
    if not filtered_df.empty: st.download_button("📄 최근 검사 TXT", data=make_report_text(filtered_df.iloc[0]), file_name=f"Latest_{filtered_df.iloc[0]['battery_id']}.txt", use_container_width=True)
with d4:
    if st.button("⚠ 전체 이력 초기화", use_container_width=True):
        clear_reports()
        st.rerun()