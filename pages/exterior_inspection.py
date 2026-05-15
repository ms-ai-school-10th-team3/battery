import base64
import textwrap
from datetime import datetime

import pandas as pd
import streamlit as st
from components.sidebar import render_sidebar
from utils.report_storage import save_inspection_report


# =========================
# Page Config
# =========================
st.set_page_config(
    page_title="Exterior Inspection",
    page_icon="🔍",
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
# Session State
# =========================
if "analysis_done" not in st.session_state:
    st.session_state.analysis_done = False

if "memo_text" not in st.session_state:
    st.session_state.memo_text = ""

if "inspection_history" not in st.session_state:
    st.session_state.inspection_history = []

if "activity_logs" not in st.session_state:
    st.session_state.activity_logs = []

if "saved_upload_signature" not in st.session_state:
    st.session_state.saved_upload_signature = None


# =========================
# CSS
# =========================
html("""
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

div[data-testid="stVerticalBlock"] {
    gap: 0.65rem;
}

label {
    font-size: 13px !important;
    color: #334155 !important;
    font-weight: 700 !important;
}

div[data-baseweb="input"] input {
    font-size: 14px !important;
}

div[data-baseweb="select"] > div,
div[data-baseweb="input"] {
    border-radius: 10px !important;
}

.stButton > button {
    width: 100%;
    height: 44px;
    border-radius: 10px;
    border: 1px solid #D7E1F2;
    background: #FFFFFF;
    color: #111827;
    font-weight: 800;
    font-size: 14px;
}

.stButton > button:hover {
    border-color: #0B63FF;
    color: #0B63FF;
}

div[data-testid="stButton"] button[kind="primary"] {
    background: #0B63FF !important;
    color: white !important;
    border: 1px solid #0B63FF !important;
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
    margin-bottom: 20px;
}

.metric-card {
    height: 116px;
    background: #FFFFFF;
    border: 1px solid #E4EAF3;
    border-radius: 16px;
    padding: 19px 21px;
    box-shadow: 0 8px 22px rgba(15, 23, 42, 0.05);
    display: flex;
    align-items: center;
    gap: 18px;
}

.metric-icon {
    width: 58px;
    height: 58px;
    border-radius: 50%;
    display: flex;
    justify-content: center;
    align-items: center;
    font-size: 27px;
    font-weight: 900;
}

.icon-blue { background: #EAF2FF; color: #0B63FF; }
.icon-green { background: #DCFCE7; color: #16A34A; }
.icon-red { background: #FEE2E2; color: #EF4444; }
.icon-purple { background: #F3E8FF; color: #7E22CE; }

.metric-label {
    font-size: 14px;
    font-weight: 800;
    color: #334155;
    margin-bottom: 4px;
}

.metric-value {
    font-size: 28px;
    font-weight: 950;
    color: #0F172A;
    line-height: 1.1;
}

.metric-sub {
    font-size: 14px;
    color: #64748B;
    margin-top: 7px;
}

.up,
.down {
    color: #0B63FF;
    font-weight: 900;
}

.upload-box {
    border: 1.5px dashed #9FC2FF;
    border-radius: 15px;
    background: #FBFDFF;
    padding: 18px 20px;
    display: flex;
    align-items: center;
    gap: 16px;
    margin-bottom: 10px;
}

.upload-icon {
    font-size: 36px;
    color: #0B63FF;
}

.upload-title {
    font-size: 18px;
    font-weight: 950;
    color: #0F172A;
}

.upload-desc {
    font-size: 14px;
    color: #64748B;
    margin-top: 4px;
}

div[data-testid="stFileUploader"] {
    background: #FFFFFF;
    border: 1px solid #E5EAF3;
    border-radius: 12px;
    padding: 10px 14px;
}

div[data-testid="stFileUploader"] section {
    border: none !important;
    background: transparent !important;
    padding: 0 !important;
}

div[data-testid="stFileUploader"] button {
    background: #FFFFFF !important;
    color: #111827 !important;
    border: 1px solid #D7E1F2 !important;
    border-radius: 8px !important;
    font-weight: 800 !important;
}

.viewer-card {
    background: #0B0F16;
    border-radius: 13px;
    overflow: hidden;
    border: 1px solid #1F2937;
    height: 420px;
    position: relative;
    box-shadow: 0 8px 22px rgba(15, 23, 42, 0.12);
}

.viewer-img {
    width: 100%;
    height: 420px;
    object-fit: cover;
    display: block;
    opacity: 0.96;
}

.viewer-placeholder {
    height: 420px;
    background: linear-gradient(135deg, #111827, #020617);
    display: flex;
    justify-content: center;
    align-items: center;
    color: #94A3B8;
    font-size: 18px;
    font-weight: 800;
}

.zoom-box {
    position: absolute;
    top: 16px;
    left: 16px;
    background: rgba(15, 23, 42, 0.82);
    color: #FFFFFF;
    border: 1px solid rgba(255,255,255,0.12);
    border-radius: 8px;
    padding: 9px 14px;
    font-size: 14px;
    font-weight: 800;
    display: flex;
    gap: 13px;
    align-items: center;
    z-index: 3;
}

.defect-point {
    position: absolute;
    width: 25px;
    height: 25px;
    border: 3px solid #FF3B3B;
    border-radius: 50%;
    background: rgba(255, 59, 59, 0.18);
    box-shadow: 0 0 0 4px rgba(255, 59, 59, 0.18);
    z-index: 3;
}

.point1 { top: 29%; left: 54%; }
.point2 { top: 49%; left: 61%; }
.point3 { top: 62%; left: 62%; }

.thumbnail-row {
    position: absolute;
    left: 145px;
    right: 72px;
    bottom: 16px;
    display: flex;
    gap: 8px;
    align-items: center;
    z-index: 3;
}

.thumb {
    width: 104px;
    height: 47px;
    border-radius: 7px;
    border: 1px solid rgba(255,255,255,0.18);
    background: rgba(255,255,255,0.08);
    overflow: hidden;
}

.thumb.active {
    border: 2px solid #0B93FF;
}

.thumb img {
    width: 100%;
    height: 100%;
    object-fit: cover;
}

.arrow-left,
.arrow-right {
    position: absolute;
    bottom: 18px;
    width: 44px;
    height: 44px;
    background: rgba(15, 23, 42, 0.75);
    color: white;
    border-radius: 9px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 22px;
    font-weight: 800;
    z-index: 3;
}

.arrow-left { left: 96px; }
.arrow-right { right: 42px; }

div[data-testid="stTabs"] {
    background: #FFFFFF;
    border: 1px solid #E4EAF3;
    border-radius: 16px;
    padding: 20px 18px;
    min-height: 420px;
    box-shadow: 0 8px 22px rgba(15, 23, 42, 0.05);
}

div[data-testid="stTabs"] button {
    font-weight: 900 !important;
    color: #475569 !important;
}

.result-box {
    border: 1px solid #E4EAF3;
    border-radius: 10px;
    padding: 14px 14px;
    margin-bottom: 10px;
    background: #FFFFFF;
}

.result-line {
    display: flex;
    justify-content: space-between;
    align-items: center;
}

.result-label {
    font-size: 14px;
    font-weight: 850;
    color: #334155;
}

.fail-text {
    color: #EF1C1C;
    font-size: 28px;
    font-weight: 950;
}

.confidence {
    color: #0B63FF;
    font-size: 16px;
    font-weight: 950;
}

.reason-list {
    font-size: 14px;
    line-height: 2.0;
    font-weight: 700;
    color: #1F2937;
}

.reason-alert {
    color: #EF4444;
    margin-right: 6px;
}

.gauge-wrap {
    position: relative;
    height: 112px;
    margin-top: 6px;
}

.gauge-bg {
    position: absolute;
    width: 190px;
    height: 95px;
    left: 50%;
    top: 8px;
    transform: translateX(-50%);
    border-radius: 190px 190px 0 0;
    background: conic-gradient(
        from 270deg,
        #EF4444 0deg 147deg,
        #E5E7EB 147deg 180deg,
        transparent 180deg 360deg
    );
}

.gauge-inner {
    position: absolute;
    width: 132px;
    height: 66px;
    left: 50%;
    top: 37px;
    transform: translateX(-50%);
    border-radius: 132px 132px 0 0;
    background: #FFFFFF;
}

.gauge-score {
    position: absolute;
    top: 54px;
    left: 0;
    right: 0;
    text-align: center;
    font-size: 34px;
    font-weight: 950;
    color: #0F172A;
}

.gauge-left {
    position: absolute;
    left: 28%;
    bottom: 6px;
    font-size: 12px;
    font-weight: 800;
    color: #334155;
}

.gauge-right {
    position: absolute;
    right: 20%;
    bottom: 6px;
    font-size: 12px;
    font-weight: 800;
    color: #334155;
}

.section-card {
    background: #FFFFFF;
    border: 1px solid #E4EAF3;
    border-radius: 16px;
    padding: 18px;
    box-shadow: 0 8px 22px rgba(15, 23, 42, 0.05);
}

.section-head {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 14px;
}

.section-title {
    font-size: 17px;
    font-weight: 950;
    color: #0F172A;
}

.link-text {
    font-size: 13px;
    color: #0B63FF;
    font-weight: 900;
}

.log-table-head {
    font-size: 13px;
    color: #64748B;
    font-weight: 900;
    padding: 8px 0;
    border-bottom: 1px solid #E5EAF3;
}

.log-cell {
    font-size: 14px;
    color: #334155;
    font-weight: 800;
    padding: 8px 0;
}

.empty-box {
    height: 140px;
    border: 1px dashed #CBD5E1;
    border-radius: 12px;
    display: flex;
    align-items: center;
    justify-content: center;
    color: #64748B;
    font-size: 14px;
    font-weight: 800;
    background: #FBFDFF;
}

textarea {
    border-radius: 12px !important;
}
</style>
""")


# =========================
# Functions
# =========================
def metric_card(title, value, sub, icon, color_class):
    html(f"""
    <div class="metric-card">
        <div class="metric-icon {color_class}">{icon}</div>
        <div>
            <div class="metric-label">{title}</div>
            <div class="metric-value">{value}</div>
            <div class="metric-sub">{sub}</div>
        </div>
    </div>
    """)


def uploaded_file_to_base64(uploaded_file):
    if uploaded_file is None:
        return None

    file_bytes = uploaded_file.getvalue()
    encoded = base64.b64encode(file_bytes).decode("utf-8")
    mime_type = uploaded_file.type or "image/png"
    return f"data:{mime_type};base64,{encoded}"


def save_inspection_record(uploaded_file, selected_line):
    now = datetime.now()
    battery_id = f"B-{len(st.session_state.inspection_history) + 1:03d}"
    file_signature = f"{uploaded_file.name}-{uploaded_file.size}"

    if st.session_state.saved_upload_signature == file_signature:
        return

    st.session_state.saved_upload_signature = file_signature

    operator = st.session_state.get("user_id", "Guest")

    record = {
        "배터리 ID": battery_id,
        "파일명": uploaded_file.name,
        "판정 결과": "불량",
        "위험도": "82%",
        "신뢰도": "92%",
        "검사 완료 시간": now.strftime("%Y-%m-%d %H:%M:%S"),
        "작업자": operator,
        "라인": selected_line,
    }

    log = {
        "시간": now.strftime("%H:%M"),
        "내용": f"{battery_id} 검사 완료",
        "판정 결과": "불량",
        "신뢰도": "92%",
        "작업자": operator,
    }

    st.session_state.inspection_history.insert(0, record)
    st.session_state.activity_logs.insert(0, log)

    save_inspection_report(
        battery_id=battery_id,
        inspection_type="외관 검사",
        result="불량",
        risk_score=82,
        operator=operator,
        line=selected_line,
        confidence=92,
        defect_summary="Swelling 의심, 표면 찌그러짐 감지, 배터리 외벽 손상",
        recommendation="격리 보관 후 원인 분석 및 교체 권장",
        model_version="Exterior-CNN-v1",
    )


def render_viewer(uploaded_file):
    image_src = uploaded_file_to_base64(uploaded_file)

    if image_src:
        defect_points = ""
        if st.session_state.analysis_done:
            defect_points = """
            <div class="defect-point point1"></div>
            <div class="defect-point point2"></div>
            <div class="defect-point point3"></div>
            """

        thumbnails = ""
        for i in range(6):
            active_class = "active" if i == 1 else ""
            thumbnails += f"""
            <div class="thumb {active_class}">
                <img src="{image_src}" />
            </div>
            """

        html(f"""
        <div class="viewer-card">
            <img class="viewer-img" src="{image_src}" />

            <div class="zoom-box">
                <span>−</span>
                <span>|</span>
                <span>100%</span>
                <span>＋</span>
                <span>|</span>
                <span>⛶</span>
            </div>

            {defect_points}

            <div class="arrow-left">‹</div>
            <div class="thumbnail-row">
                {thumbnails}
            </div>
            <div class="arrow-right">›</div>
        </div>
        """)
    else:
        html("""
        <div class="viewer-card">
            <div class="zoom-box">
                <span>−</span>
                <span>|</span>
                <span>100%</span>
                <span>＋</span>
                <span>|</span>
                <span>⛶</span>
            </div>
            <div class="viewer-placeholder">
                Exterior Battery Image Preview
            </div>
        </div>
        """)


def render_result_content():
    if st.session_state.analysis_done:
        html("""
        <div class="result-box">
            <div class="result-line">
                <span class="result-label">판정 결과</span>
                <span class="fail-text">불량</span>
                <span class="confidence">신뢰도 92%</span>
            </div>
        </div>

        <div class="result-box">
            <div class="reason-list">
                <b>불량 이유</b><br>
                <span class="reason-alert">△</span> Swelling 의심<br>
                <span class="reason-alert">△</span> 표면 찌그러짐 감지<br>
                <span class="reason-alert">△</span> 배터리 외벽 손상
            </div>
        </div>

        <div class="result-box">
            <div class="result-label">위험도</div>
            <div class="fail-text" style="font-size:26px; margin-top:8px;">높음</div>
            <div class="gauge-wrap">
                <div class="gauge-bg"></div>
                <div class="gauge-inner"></div>
                <div class="gauge-score">82%</div>
                <div class="gauge-left">0%</div>
                <div class="gauge-right">100%</div>
            </div>
        </div>

        <div class="result-box">
            <div style="display:grid; grid-template-columns:1fr 1.6fr; gap:8px; font-size:14px; line-height:1.8;">
                <b>검사 시간</b>
                <div>
                    분석 소요 시간&nbsp;&nbsp; <b>1.8초</b><br>
                    검사 완료 시간&nbsp;&nbsp; <b>2026-05-13 14:32</b>
                </div>
            </div>
        </div>
        """)
    else:
        html("""
        <div class="result-box" style="height:310px; display:flex; align-items:center; justify-content:center; text-align:center;">
            <div style="color:#64748B; font-weight:800; line-height:1.7;">
                이미지를 업로드한 뒤<br>
                <span style="color:#0B63FF;">AI 분석 시작</span> 버튼을 눌러주세요.
            </div>
        </div>
        """)


def render_image_info(uploaded_file):
    if uploaded_file:
        file_size = round(uploaded_file.size / 1024, 2)
        html(f"""
        <div class="result-box">
            <div style="line-height:2.1; font-size:14px;">
                <b>파일명</b><br>{uploaded_file.name}<br><br>
                <b>파일 크기</b><br>{file_size} KB<br><br>
                <b>파일 타입</b><br>{uploaded_file.type}<br><br>
                <b>업로드 상태</b><br>업로드 완료
            </div>
        </div>
        """)
    else:
        html("""
        <div class="result-box" style="height:250px; display:flex; align-items:center; justify-content:center;">
            <div style="color:#64748B; font-weight:800;">업로드된 이미지가 없습니다.</div>
        </div>
        """)


def render_detail_data():
    detail_df = pd.DataFrame(
        {
            "항목": ["Model", "Prediction", "Confidence", "Risk Score", "Defect Count"],
            "값": ["Exterior-CNN-v1", "Defect", "92%", "82%", "3"],
        }
    )
    st.dataframe(detail_df, use_container_width=True, hide_index=True)


def render_result_panel(uploaded_file):
    tab1, tab2, tab3 = st.tabs(["분석 결과", "이미지 정보", "상세 데이터"])

    with tab1:
        render_result_content()

    with tab2:
        render_image_info(uploaded_file)

    with tab3:
        render_detail_data()


def render_history_table(df):
    html("""
    <div class="section-card">
        <div class="section-head">
            <div class="section-title">최근 검사 이력</div>
            <div class="link-text">전체 보기</div>
        </div>
    """)

    if df.empty:
        html("""
        <div class="empty-box">
            아직 저장된 검사 이력이 없습니다.
        </div>
        </div>
        """)
        return

    html("</div>")

    st.dataframe(
        df[
            [
                "배터리 ID",
                "파일명",
                "판정 결과",
                "위험도",
                "신뢰도",
                "검사 완료 시간",
                "작업자",
            ]
        ],
        use_container_width=True,
        hide_index=True,
    )


def render_log_box():
    html("""
    <div class="section-card">
        <div class="section-head">
            <div class="section-title">활동 로그 / 메모</div>
            <div class="link-text">✎ 메모 작성</div>
        </div>
    """)

    if not st.session_state.activity_logs:
        html("""
        <div class="empty-box">
            아직 활동 로그가 없습니다.
        </div>
        </div>
        """)
        return

    html("</div>")

    h1, h2, h3, h4, h5 = st.columns([0.8, 1.8, 1, 1, 1])
    with h1:
        html('<div class="log-table-head">시간</div>')
    with h2:
        html('<div class="log-table-head">내용</div>')
    with h3:
        html('<div class="log-table-head">판정</div>')
    with h4:
        html('<div class="log-table-head">신뢰도</div>')
    with h5:
        html('<div class="log-table-head">작업자</div>')

    for log in st.session_state.activity_logs:
        c1, c2, c3, c4, c5 = st.columns([0.8, 1.8, 1, 1, 1])

        with c1:
            html(f'<div class="log-cell">{log["시간"]}</div>')

        with c2:
            html(f'<div class="log-cell">{log["내용"]}</div>')

        with c3:
            if log["판정 결과"] == "불량":
                st.error(log["판정 결과"])
            else:
                st.success(log["판정 결과"])

        with c4:
            html(f'<div class="log-cell">{log["신뢰도"]}</div>')

        with c5:
            html(f'<div class="log-cell">{log["작업자"]}</div>')


# =========================
# Sidebar
# =========================
render_sidebar("exterior")


# =========================
# Top Area
# =========================
top_left, top_right = st.columns([2.35, 1.65])

with top_left:
    html("""
    <div class="main-title">AI 배터리 외관 검사</div>
    """)
    html("""
    <div class="sub-title">
        배터리 외관 이미지를 업로드하면 AI가 정상/불량 여부, 손상 위치, 위험도를 분석합니다.
    </div>
    """)

with top_right:
    f1, f2, f3 = st.columns([1, 1, 1.45])

    with f1:
        selected_date = st.date_input(
            "날짜",
            value=datetime.today(),
            label_visibility="collapsed",
        )

    with f2:
        selected_line = st.selectbox(
            "라인",
            ["전체 라인", "A Line", "B Line", "C Line"],
            label_visibility="collapsed",
        )

    with f3:
        search_id = st.text_input(
            "검색",
            placeholder="배터리 ID 검색",
            label_visibility="collapsed",
        )


# =========================
# Metric Cards
# =========================
m1, m2, m3, m4 = st.columns(4)

with m1:
    metric_card(
        "오늘 전체 검사 수",
        "1,248 건",
        '전일 대비 <span class="up">↑ 12.5%</span>',
        "▣",
        "icon-blue",
    )

with m2:
    metric_card("정상", "982 건", "78.8%", "✓", "icon-green")

with m3:
    metric_card("불량", "266 건", "21.2%", "△", "icon-red")

with m4:
    metric_card(
        "평균 검사 시간",
        "1.8 초",
        '전일 대비 <span class="down">↓ 0.2초</span>',
        "◷",
        "icon-purple",
    )


html("<div style='height:10px;'></div>")


# =========================
# Upload + Viewer + Result
# =========================
main_left, main_right = st.columns([2.35, 1])

with main_left:
    html("""
    <div class="upload-box">
        <div class="upload-icon">☁</div>
        <div>
            <div class="upload-title">이미지 업로드</div>
            <div class="upload-desc">이미지를 드래그 앤 드롭 하거나 파일을 선택하세요. (JPG, PNG)</div>
        </div>
    </div>
    """)

    upload_col, analyze_col = st.columns([4, 1])

    with upload_col:
        uploaded_file = st.file_uploader(
            "파일 선택",
            type=["jpg", "jpeg", "png"],
            label_visibility="collapsed",
        )

    with analyze_col:
        analyze_clicked = st.button(
            "✣ AI 분석 시작",
            key="analyze_btn",
            type="primary",
        )

    if uploaded_file is None:
        st.session_state.analysis_done = False
        st.session_state.saved_upload_signature = None

    if analyze_clicked:
        if uploaded_file:
            st.session_state.analysis_done = True
            save_inspection_record(uploaded_file, selected_line)
            st.success("AI 분석이 완료되었습니다. 최근 검사 이력, 활동 로그, 보고서에 저장되었습니다.")
        else:
            st.warning("먼저 이미지를 업로드해주세요.")

    render_viewer(uploaded_file)

with main_right:
    render_result_panel(uploaded_file)


html("<div style='height:10px;'></div>")


# =========================
# Bottom Area
# =========================
history_df = pd.DataFrame(st.session_state.inspection_history)

if history_df.empty:
    filtered_df = history_df
else:
    filtered_df = history_df.copy()

    if selected_line != "전체 라인":
        filtered_df = filtered_df[filtered_df["라인"] == selected_line]

    if search_id.strip():
        filtered_df = filtered_df[
            filtered_df["배터리 ID"].str.contains(search_id.strip(), case=False, na=False)
            | filtered_df["파일명"].str.contains(search_id.strip(), case=False, na=False)
        ]

bottom_left, bottom_right = st.columns([1, 1])

with bottom_left:
    render_history_table(filtered_df)

with bottom_right:
    render_log_box()

    with st.expander("메모 작성하기"):
        st.session_state.memo_text = st.text_area(
            "메모",
            value=st.session_state.memo_text,
            placeholder="검사 관련 메모를 입력하세요.",
            height=120,
        )

        if st.button("메모 저장"):
            if st.session_state.memo_text.strip():
                st.success("메모가 저장되었습니다.")
            else:
                st.warning("메모 내용을 입력해주세요.")
