import os
import textwrap
from datetime import datetime

import pandas as pd
import streamlit as st


# =========================
# Page Config
# =========================
st.set_page_config(
    page_title="AI Battery Inspection Report",
    page_icon="📄",
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
    "image_path",
    "heatmap_path",
    "overlay_path",
]


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


def get_selected_report():
    selected_report = st.session_state.get("selected_report")

    if selected_report:
        report = selected_report.copy()

        if "completed_at" in report:
            report["completed_at"] = pd.to_datetime(report["completed_at"], errors="coerce")

        return report

    return None


def format_datetime(value):
    if pd.isna(value):
        return "-"

    if isinstance(value, pd.Timestamp):
        return value.strftime("%Y-%m-%d %H:%M")

    return str(value)


def get_risk_level(score):
    try:
        score = int(score)
    except Exception:
        return "알 수 없음"

    if score >= 70:
        return "높음"
    if score >= 40:
        return "주의"
    return "낮음"


def safe_text(value, default="-"):
    if value is None:
        return default

    if pd.isna(value):
        return default

    value = str(value).strip()

    if not value:
        return default

    return value


# =========================
# CSS
# =========================
html("""
<style>
.stApp {
    background: #F8FBFF;
    color: #111827;
}

header[data-testid="stHeader"] {
    background-color: rgba(0,0,0,0) !important;
}

footer, #MainMenu {
    visibility: hidden;
}

.block-container {
    padding: 1.6rem 2.4rem;
    max-width: 100%;
}

[data-testid="stSidebar"] {
    background-color: #FFFFFF !important;
    border-right: 1px solid #E5EAF3 !important;
}

[data-testid="stSidebarUserContent"] {
    padding-top: 2rem !important;
    padding-left: 1rem !important;
    padding-right: 1rem !important;
}

div[data-testid="stSidebarUserContent"] div.stPageLink,
div[data-testid="stSidebarUserContent"] div.stPageLink a {
    background: transparent !important;
    background-color: transparent !important;
    border: none !important;
    box-shadow: none !important;
    text-decoration: none !important;
}

div[data-testid="stSidebarUserContent"] div.stPageLink a:hover {
    background-color: #F1F5F9 !important;
    border-radius: 10px !important;
}

.sidebar-logo-area {
    margin-bottom: 30px;
    padding-left: 8px;
}

.sidebar-title {
    font-size: 21px;
    font-weight: 800;
    color: #0F172A;
    display: flex;
    align-items: center;
    gap: 10px;
}

.sidebar-logo-icon {
    width: 20px;
    height: 24px;
    background: #3B82F6;
    border-radius: 4px 4px 10px 10px;
    display: inline-block;
}

.sidebar-subtitle {
    font-size: 12px;
    font-weight: 600;
    color: #64748B;
    margin-top: 4px;
    padding-left: 30px;
}

.operator-card {
    border: 1px solid #E5EAF3;
    border-radius: 16px;
    padding: 16px;
    background: #FFFFFF;
    margin-top: 40px;
}

.operator-title {
    font-size: 13.5px;
    font-weight: 700;
    color: #475569;
    margin-bottom: 10px;
}

.operator-name {
    font-size: 16px;
    font-weight: 800;
    color: #0F172A;
    margin-bottom: 16px;
    padding-left: 22px;
}

.operator-time {
    font-size: 11px;
    color: #64748B;
    padding-left: 22px;
    font-weight: 600;
}

.main-title {
    font-size: 34px;
    font-weight: 950;
    color: #0F172A;
    letter-spacing: -0.8px;
    margin-bottom: 18px;
}

.card {
    background: #FFFFFF;
    border: 1px solid #E4EAF3;
    border-radius: 16px;
    padding: 20px;
    box-shadow: 0 8px 22px rgba(15, 23, 42, 0.05);
    margin-bottom: 14px;
}

.label {
    font-size: 13px;
    color: #64748B;
    font-weight: 800;
    margin-bottom: 6px;
}

.value {
    font-size: 22px;
    color: #0F172A;
    font-weight: 950;
}

.small-value {
    font-size: 17px;
    color: #0F172A;
    font-weight: 850;
}

.result-badge {
    display: inline-block;
    padding: 9px 18px;
    border-radius: 10px;
    font-size: 22px;
    font-weight: 950;
}

.result-badge-fail {
    color: #DC2626;
    background: #FEE2E2;
    border: 1px solid #FCA5A5;
}

.result-badge-normal {
    color: #1D4ED8;
    background: #DBEAFE;
    border: 1px solid #93C5FD;
}

.section-title {
    font-size: 22px;
    font-weight: 950;
    color: #0F172A;
    margin: 12px 0 12px 0;
}

.image-placeholder {
    height: 360px;
    border-radius: 16px;
    border: 1px dashed #CBD5E1;
    background: linear-gradient(135deg, #EEF6FF, #F8FBFF);
    display: flex;
    align-items: center;
    justify-content: center;
    color: #64748B;
    font-weight: 850;
    text-align: center;
}

.summary-line {
    font-size: 18px;
    font-weight: 850;
    margin-bottom: 14px;
    color: #111827;
}

.summary-danger {
    color: #DC2626;
    font-weight: 950;
}

.summary-normal {
    color: #1D4ED8;
    font-weight: 950;
}

.risk-score {
    font-size: 48px;
    font-weight: 950;
    color: #DC2626;
    text-align: center;
    margin: 18px 0 2px 0;
}

.risk-caption {
    text-align: center;
    font-weight: 850;
    color: #DC2626;
    margin-bottom: 18px;
}

/* 전체 버튼 기본 스타일 */
div.stButton > button {
    height: 42px !important;
    border-radius: 10px !important;
    font-weight: 850 !important;
    background-color: #FFFFFF !important;
    color: #0F172A !important;
    border: 1px solid #CBD5E1 !important;
    box-shadow: none !important;
}

div.stButton > button:hover {
    background-color: #EFF6FF !important;
    color: #0B63FF !important;
    border-color: #93C5FD !important;
}

/* 로그아웃 버튼 */
div.logout-btn-wrap div.stButton > button {
    width: 100% !important;
    height: 42px !important;
    border: 1px solid #E5EAF3 !important;
    border-radius: 12px !important;
    background: #FFFFFF !important;
    color: #475569 !important;
    font-weight: 700 !important;
    font-size: 14px !important;
    box-shadow: none !important;
    margin-top: 12px;
}

div.logout-btn-wrap div.stButton > button:hover {
    border-color: #3B82F6 !important;
    color: #3B82F6 !important;
    background: #F8FAFC !important;
}

/* 닫기 버튼 강조 */
div[data-testid="column"]:last-child div.stButton > button {
    font-size: 18px !important;
}
</style>
""")


# =========================
# Sidebar
# =========================
with st.sidebar:
    html("""
    <div class="sidebar-logo-area">
        <div class="sidebar-title">
            <span class="sidebar-logo-icon"></span>
            CellGuard AI
        </div>
        <div class="sidebar-subtitle">Battery Inspection</div>
    </div>
    """)

    st.page_link("pages/exterior_inspection.py", label="🔍 Exterior Inspection", use_container_width=True)
    st.page_link("pages/ct_inspection.py", label="☢ CT Inspection", use_container_width=True)
    st.page_link("pages/inspection_report.py", label="📋 Inspection Report", use_container_width=True)

    now_str = datetime.now().strftime("%Y-%m-%d %H:%M")
    operator_name = st.session_state.get("operator", "1")

    html(f"""
    <div class="operator-card">
        <div class="operator-title">👤 Operator</div>
        <div class="operator-name">{operator_name}</div>
        <div class="operator-time">Access Time: {now_str}</div>
    </div>
    """)

    st.markdown('<div class="logout-btn-wrap">', unsafe_allow_html=True)

    if st.button("Logout", key="btn_logout"):
        st.session_state.login = False
        st.switch_page("streamlit_app.py")

    st.markdown("</div>", unsafe_allow_html=True)


# =========================
# Selected Report
# =========================
report = get_selected_report()

if report is None:
    st.warning("선택된 보고서가 없습니다. 검사 이력 페이지에서 보고서를 선택해주세요.")

    nav1, nav2 = st.columns([1, 5])

    with nav1:
        if st.button("← 이력으로", key="btn_empty_back"):
            st.switch_page("pages/inspection_report.py")

    st.stop()


# =========================
# Main Header
# =========================
top_nav_left, top_nav_right = st.columns([6, 1])

with top_nav_left:
    if st.button("← 보고서 이력으로 돌아가기", key="btn_back_to_reports"):
        st.switch_page("pages/inspection_report.py")

with top_nav_right:
    if st.button("✕ 닫기", key="btn_close_report", use_container_width=True):
        st.switch_page("pages/inspection_report.py")

st.markdown('<div class="main-title">AI 배터리 검사 상세 보고서</div>', unsafe_allow_html=True)


# =========================
# Report Values
# =========================
battery_id = safe_text(report.get("battery_id"))
inspection_type = safe_text(report.get("inspection_type"))
result = safe_text(report.get("result"))
risk_score = int(report.get("risk_score", 0))
confidence = int(report.get("confidence", 0))
completed_text = format_datetime(report.get("completed_at"))
operator = safe_text(report.get("operator"))
line = safe_text(report.get("line"))
model_version = safe_text(report.get("model_version"))
defect_summary = safe_text(report.get("defect_summary"), "결함 정보 없음")
recommendation = safe_text(report.get("recommendation"), "격리 보관 후 정밀 분석 필요")
risk_level = get_risk_level(risk_score)

badge_class = "result-badge-fail" if result == "불량" else "result-badge-normal"
result_color_class = "summary-danger" if result == "불량" else "summary-normal"


# =========================
# Top Summary
# =========================
top1, top2, top3 = st.columns([1.1, 0.8, 2])

with top1:
    html(f"""
    <div class="card">
        <div class="label">배터리 ID</div>
        <div class="value">{battery_id}</div>
    </div>
    """)

with top2:
    html(f"""
    <div class="card">
        <div class="label">판정 결과</div>
        <span class="result-badge {badge_class}">{result}</span>
    </div>
    """)

with top3:
    html(f"""
    <div class="card">
        <div class="label">검사 일시</div>
        <div class="value">{completed_text}</div>
    </div>
    """)


# =========================
# Meta Info
# =========================
m1, m2, m3, m4, m5 = st.columns(5)

meta_items = [
    ("라인", line),
    ("검사 유형", inspection_type),
    ("운전자", operator),
    ("AI Model 버전", model_version),
    ("신뢰도", f"{confidence}%"),
]

for col, (label, value) in zip([m1, m2, m3, m4, m5], meta_items):
    with col:
        html(f"""
        <div class="card">
            <div class="label">{label}</div>
            <div class="small-value">{value}</div>
        </div>
        """)


# =========================
# Detail Result
# =========================
st.markdown('<div class="section-title">2. 상세 분석 결과</div>', unsafe_allow_html=True)

left, right = st.columns([2.4, 1])

with left:
    image_url = report.get("image_url", "")
    image_path = report.get("image_path", "")
    overlay_path = report.get("overlay_path", "")

    if isinstance(overlay_path, str) and overlay_path.strip() and os.path.exists(overlay_path):
        st.image(overlay_path, use_container_width=True)

    elif isinstance(image_url, str) and image_url.strip():
        st.image(image_url, use_container_width=True)

    elif isinstance(image_path, str) and image_path.strip() and os.path.exists(image_path):
        st.image(image_path, use_container_width=True)

    else:
        st.markdown(
            """
            <div class="image-placeholder">
                원본 이미지 / AI 검출 시각화 영역<br>
                검사 이미지 또는 AI overlay 결과를 표시합니다.
            </div>
            """,
            unsafe_allow_html=True,
        )

with right:
    with st.container(border=True):
        st.markdown(
            f"""
            <div class="summary-line">
                * 판정 결과 :
                <span class="{result_color_class}">{result}</span>
                (신뢰도 {confidence}%)
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.markdown("**위험도**")
        st.markdown(
            f"""
            <div class="risk-score">{risk_score}%</div>
            <div class="risk-caption">{risk_level}</div>
            """,
            unsafe_allow_html=True,
        )

        st.markdown("**상세 불량 사유**")

        if result == "불량":
            st.error(defect_summary)
        else:
            st.success(defect_summary)

        st.markdown("**조치 참고**")
        st.info(recommendation)


# =========================
# Deep Data & Log
# =========================
g1, g2 = st.columns([1.6, 1])

with g1:
    st.markdown('<div class="section-title">3. 심층 데이터 및 그래프</div>', unsafe_allow_html=True)

    chart_df = pd.DataFrame({
        "항목": ["위험도", "신뢰도"],
        "점수": [risk_score, confidence],
    })

    st.bar_chart(chart_df.set_index("항목"), height=240)

with g2:
    st.markdown('<div class="section-title">활동 로그</div>', unsafe_allow_html=True)

    with st.container(border=True):
        st.markdown(f"**{completed_text}**")
        st.caption(f"검사 완료 · AI 판정: {result}")

        st.divider()

        st.markdown("**분석 완료**")
        st.caption(f"위험도 {risk_score}% · 신뢰도 {confidence}%")

        st.divider()

        st.markdown("**보고서 생성**")
        st.caption("상세 보고서 화면에 결과 반영")