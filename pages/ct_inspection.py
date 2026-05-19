import sys
from pathlib import Path

import base64
import textwrap
from datetime import datetime

import pandas as pd
import streamlit as st
from utils.report_storage import save_inspection_report

DEEPLAB_DIR = Path("ai_models/deeplab_mobilenet").resolve()
if str(DEEPLAB_DIR) not in sys.path:
    sys.path.insert(0, str(DEEPLAB_DIR))

from predict import predict_one_image

# =========================
# 1. Page Config & Session Check
# =========================
st.set_page_config(
    page_title="CT Inspection",
    page_icon="☢️",
    layout="wide",
    initial_sidebar_state="expanded", # 첫 번째 페이지와 일관되게 순정 사이드바 확장 상태로 시작
)

if "login" not in st.session_state or not st.session_state["login"]:
    st.switch_page("streamlit_app.py")


# =========================
# HTML Helper
# =========================
def html(code):
    st.markdown(textwrap.dedent(code).strip(), unsafe_allow_html=True)


# =========================
# Session State Init
# =========================
if "ct_analysis_done" not in st.session_state:
    st.session_state.ct_analysis_done = False

if "ct_memo_text" not in st.session_state:
    st.session_state.ct_memo_text = ""

if "ct_history" not in st.session_state:
    st.session_state.ct_history = []

if "ct_saved_upload_signature" not in st.session_state:
    st.session_state.ct_saved_upload_signature = None
    
if "latest_ct_result" not in st.session_state:
    st.session_state.latest_ct_result = None

if "latest_ct_completed_at" not in st.session_state:
    st.session_state.latest_ct_completed_at = "-"
    


# =========================
# 🎨 CSS 주입 (디자인 통일 및 사이드바 출입 복원)
# =========================
html("""
<style>
/* 기본 앱 배경 설정 */
.stApp { background: #F8FBFF; color: #111827; }
header[data-testid="stHeader"] { background-color: rgba(0,0,0,0) !important; z-index: 999990 !important; }
footer, #MainMenu { visibility: hidden; }

.block-container {
    padding-top: 1.6rem;
    padding-left: 2.4rem;
    padding-right: 2.4rem;
    padding-bottom: 2rem;
    max-width: 100%;
}

/* 🌟 순정 사이드바 배경 및 테두리 완전히 플랫하게 리스타일링 */
[data-testid="stSidebar"] {
    background-color: #FFFFFF !important;
    border-right: 1px solid #E5EAF3 !important;
    z-index: 999995 !important;
}
[data-testid="stSidebarUserContent"] {
    padding-top: 2rem !important;
    padding-left: 1rem !important;
    padding-right: 1rem !important;
}

/* 🌟 사이드바가 완전히 접혔을 때 나타나는 순정 '작은 화살표 버튼(»)' 영역을 강제로 화면 최상단으로 올림 */
div[data-testid="collapsedControl"] {
    z-index: 999999 !important;
}
button[data-testid="stSidebarCollapseButton"] {
    background-color: #FFFFFF !important;
    border: 1px solid #E5EAF3 !important;
    border-radius: 8px !important;
    box-shadow: 0 2px 8px rgba(15, 23, 42, 0.08) !important;
    cursor: pointer !important;
}

/* 🌟 순정 st.page_link의 흰색 테두리 상자 조각들을 완전히 제거 */
div[data-testid="stPageLink-FormSubmitButton"] > div,
div[data-testid="stSidebarUserContent"] div.stPageLink,
div[data-testid="stSidebarUserContent"] div.stPageLink a {
    background: transparent !important;
    background-color: transparent !important;
    border: none !important;
    box-shadow: none !important;
    text-decoration: none !important;
}

/* 메뉴 아이템 호버 스타일 교정 */
div[data-testid="stSidebarUserContent"] div.stPageLink a:hover {
    background-color: #F1F5F9 !important;
    border-radius: 10px !important;
}

/* 로고 및 작업자 영역 스타일 정의 */
.sidebar-logo-area { margin-bottom: 30px; padding-left: 8px; }
.sidebar-title { font-size: 21px; font-weight: 800; color: #0F172A; display: flex; align-items: center; gap: 10px; }
.sidebar-logo-icon { width: 20px; height: 24px; background: #3B82F6; border-radius: 4px 4px 10px 10px; display: inline-block; }
.sidebar-subtitle { font-size: 12px; font-weight: 600; color: #64748B; margin-top: 4px; padding-left: 30px; }

.operator-card {
    border: 1px solid #E5EAF3; border-radius: 16px; padding: 16px; background: #FFFFFF; margin-top: 40px;
}
.operator-title { font-size: 13.5px; font-weight: 700; color: #475569; display: flex; align-items: center; gap: 8px; margin-bottom: 10px; }
.operator-name { font-size: 16px; font-weight: 800; color: #0F172A; margin-bottom: 16px; padding-left: 22px; }
.operator-time { font-size: 11px; color: #64748B; padding-left: 22px; font-weight: 600; }

/* 로그아웃 버튼 평면 테두리화 */
div.logout-btn-wrap div.stButton > button {
    width: 100% !important; height: 42px !important; border: 1px solid #E5EAF3 !important;
    border-radius: 12px !important; background: #FFFFFF !important; color: #475569 !important;
    font-weight: 700 !important; font-size: 14px !important; box-shadow: none !important; margin-top: 12px;
}
div.logout-btn-wrap div.stButton > button:hover { border-color: #3B82F6 !important; color: #3B82F6 !important; background: #F8FAFC !important; }

div[data-testid="stVerticalBlock"] { gap: 0.65rem; }
label { font-size: 13px !important; color: #334155 !important; font-weight: 700 !important; }
div[data-baseweb="input"] input { font-size: 14px !important; }
div[data-baseweb="select"] > div, div[data-baseweb="input"] { border-radius: 10px !important; }

.stButton > button {
    width: 100%; height: 44px; border-radius: 10px; border: 1px solid #D7E1F2;
    background: #FFFFFF; color: #111827; font-weight: 800; font-size: 14px;
}
.stButton > button:hover { border-color: #0B63FF; color: #0B63FF; }
div[data-testid="stButton"] button[kind="primary"] { background: #0B63FF !important; color: white !important; border: 1px solid #0B63FF !important; }

.main-title { font-size: 34px; font-weight: 950; color: #0F172A; margin-bottom: 6px; letter-spacing: -0.8px; }
.sub-title { font-size: 15px; color: #475569; margin-bottom: 20px; }

.metric-card {
    height: 116px; background: #FFFFFF; border: 1px solid #E4EAF3; border-radius: 16px; padding: 19px 21px;
    box-shadow: 0 8px 22px rgba(15, 23, 42, 0.05); display: flex; align-items: center; gap: 18px;
}
.metric-icon { width: 58px; height: 58px; border-radius: 50%; display: flex; justify-content: center; align-items: center; font-size: 27px; font-weight: 900; }
.icon-blue { background: #EAF2FF; color: #0B63FF; }
.icon-green { background: #DCFCE7; color: #16A34A; }
.icon-red { background: #FEE2E2; color: #EF4444; }
.icon-purple { background: #F3E8FF; color: #7E22CE; }
.metric-label { font-size: 14px; font-weight: 800; color: #334155; margin-bottom: 4px; }
.metric-value { font-size: 28px; font-weight: 950; color: #0F172A; line-height: 1.1; }
.metric-sub { font-size: 14px; color: #64748B; margin-top: 7px; }
.up, .down { color: #0B63FF; font-weight: 900; }

.upload-box {
    border: 1.5px dashed #9FC2FF; border-radius: 15px; background: #FBFDFF; padding: 18px 20px;
    display: flex; align-items: center; gap: 16px; margin-bottom: 10px;
}
.upload-icon { font-size: 36px; color: #0B63FF; }
.upload-title { font-size: 18px; font-weight: 950; color: #0F172A; }
.upload-desc { font-size: 14px; color: #64748B; margin-top: 4px; }

div[data-testid="stFileUploader"] { background: #FFFFFF; border: 1px solid #E5EAF3; border-radius: 12px; padding: 10px 14px; }
div[data-testid="stFileUploader"] section { border: none !important; background: transparent !important; padding: 0 !important; }
div[data-testid="stFileUploader"] button { background: #FFFFFF !important; color: #111827 !important; border: 1px solid #D7E1F2 !important; border-radius: 8px !important; font-weight: 800 !important; }

.viewer-card { border-radius: 13px; overflow: hidden; border: 1px solid #1F2937; height: 420px; position: relative; box-shadow: 0 8px 22px rgba(15, 23, 42, 0.12); }
.viewer-img { width: 100%; height: 420px; object-fit: cover; display: block; opacity: 0.96; }
.viewer-placeholder { height: 420px; background: linear-gradient(135deg, #111827, #020617); display: flex; justify-content: center; align-items: center; color: #94A3B8; font-size: 18px; font-weight: 800; text-align: center; line-height: 1.7; }
.zoom-box { position: absolute; top: 16px; left: 16px; background: rgba(15, 23, 42, 0.82); color: #FFFFFF; border: 1px solid rgba(255,255,255,0.12); border-radius: 8px; padding: 9px 14px; font-size: 14px; font-weight: 800; display: flex; gap: 13px; align-items: center; z-index: 3; }

.defect-point { position: absolute; width: 25px; height: 25px; border: 3px solid #FF3B3B; border-radius: 50%; background: rgba(255, 59, 59, 0.18); box-shadow: 0 0 0 4px rgba(255, 59, 59, 0.18); z-index: 3; }
.point1 { top: 24%; left: 58%; } .point2 { top: 46%; left: 66%; } .point3 { top: 62%; left: 58%; }
.slice-arc { position: absolute; top: 25%; left: 58.6%; width: 120px; height: 205px; border-right: 2px dashed rgba(255, 46, 46, 0.5); border-radius: 0 120px 120px 0; z-index: 2; }
.thumbnail-row { position: absolute; left: 145px; right: 72px; bottom: 16px; display: flex; gap: 8px; align-items: center; z-index: 3; }
.thumb { width: 104px; height: 47px; border-radius: 7px; border: 1px solid rgba(255,255,255,0.18); background: rgba(255,255,255,0.08); overflow: hidden; color: #FFFFFF; font-size: 12px; font-weight: 800; display: flex; align-items: end; justify-content: center; padding-bottom: 3px; }
.thumb.active { border: 2px solid #0B93FF; }
.thumb img { width: 100%; height: 100%; object-fit: cover; }
.arrow-left, .arrow-right { position: absolute; bottom: 18px; width: 44px; height: 44px; background: rgba(15, 23, 42, 0.75); color: white; border-radius: 9px; display: flex; align-items: center; justify-content: center; font-size: 22px; font-weight: 800; z-index: 3; }
.arrow-left { left: 96px; } .arrow-right { right: 42px; }

div[data-testid="stTabs"] { background: #FFFFFF; border: 1px solid #E4EAF3; border-radius: 16px; padding: 20px 18px; min-height: 420px; box-shadow: 0 8px 22px rgba(15, 23, 42, 0.05); }
div[data-testid="stTabs"] button { font-weight: 900 !important; color: #475569 !important; }

.result-box { border: 1px solid #E4EAF3; border-radius: 10px; padding: 14px 14px; margin-bottom: 10px; background: #FFFFFF; }
.result-line { display: flex; justify-content: space-between; align-items: center; }
.result-label { font-size: 14px; font-weight: 850; color: #334155; }
.fail-text { color: #EF1C1C; font-size: 28px; font-weight: 950; }
.success-text { color: #16A34A; font-size: 28px; font-weight: 950; }
.confidence { color: #0B63FF; font-size: 16px; font-weight: 950; }
.reason-list { font-size: 14px; line-height: 2.0; font-weight: 700; color: #1F2937; }
.reason-alert { color: #EF4444; margin-right: 6px; }

.gauge-wrap { position: relative; height: 112px; margin-top: 6px; }
.gauge-bg { position: absolute; width: 190px; height: 95px; left: 50%; top: 8px; transform: translateX(-50%); border-radius: 190px 190px 0 0; background: conic-gradient(from 270deg, #EF4444 0deg 137deg, #E5E7EB 137deg 180deg, transparent 180deg 360deg); }
.gauge-inner { position: absolute; width: 132px; height: 66px; left: 50%; top: 37px; transform: translateX(-50%); border-radius: 132px 132px 0 0; background: #FFFFFF; }
.gauge-score { position: absolute; top: 54px; left: 0; right: 0; text-align: center; font-size: 34px; font-weight: 950; color: #0F172A; }
.gauge-left { position: absolute; left: 28%; bottom: 6px; font-size: 12px; font-weight: 800; color: #334155; }
.gauge-right { position: absolute; right: 20%; bottom: 6px; font-size: 12px; font-weight: 800; color: #334155; }

.section-card { background: #FFFFFF; border: 1px solid #E4EAF3; border-radius: 16px; padding: 18px; box-shadow: 0 8px 22px rgba(15, 23, 42, 0.05); }
.section-head { display: flex; justify-content: space-between; align-items: center; margin-bottom: 14px; }
.section-title { font-size: 17px; font-weight: 950; color: #0F172A; }
.link-text { font-size: 13px; color: #0B63FF; font-weight: 900; }
.log-table-head { font-size: 13px; color: #64748B; font-weight: 900; padding: 8px 0; border-bottom: 1px solid #E5EAF3; }
.log-cell { font-size: 14px; color: #334155; font-weight: 800; padding: 8px 0; }
.empty-box { height: 140px; border: 1px dashed #CBD5E1; border-radius: 12px; display: flex; align-items: center; justify-content: center; color: #64748B; font-size: 14px; font-weight: 800; background: #FBFDFF; }
textarea { border-radius: 12px !important; }
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


def file_path_to_base64(file_path):
    file_path = Path(file_path)
    if not file_path.exists():
        return None

    suffix = file_path.suffix.lower()
    mime_type = "image/png"
    if suffix in [".jpg", ".jpeg"]:
        mime_type = "image/jpeg"

    encoded = base64.b64encode(file_path.read_bytes()).decode("utf-8")
    return f"data:{mime_type};base64,{encoded}"


def uploaded_file_to_base64(uploaded_file):
    if uploaded_file is None:
        return None
    mime_type = uploaded_file.type or ""
    if not mime_type.startswith("image/"):
        return None
    file_bytes = uploaded_file.getvalue()
    encoded = base64.b64encode(file_bytes).decode("utf-8")
    return f"data:{mime_type};base64,{encoded}"


def save_ct_record(uploaded_file, selected_line, result):
    now = datetime.now()
    ct_id = f"CT-{len(st.session_state.ct_history) + 1:03d}"
    operator = str(st.session_state.get("user_id", "1"))

    judgement = result.get("judgement", {})
    abnormal = judgement.get("abnormal", False)

    final_result = "불량" if abnormal else "정상"
    defect_types = judgement.get("defect_types", [])
    defect_summary = ", ".join(defect_types) if defect_types else "주요 결함 없음"

    defect_ratios = judgement.get("defect_ratios", {})
    risk_score = int(round(sum(float(v) for v in defect_ratios.values())))
    risk_score = min(max(risk_score, 0), 100)
    
    overlay_path = ""

    overlay_rel_path = result.get("files", {}).get("overlay")
    if overlay_rel_path:
        overlay_path = str(DEEPLAB_DIR / overlay_rel_path)

    confidence = 0.94 if abnormal else 0.85

    record = {
        "CT ID": ct_id,
        "파일명": uploaded_file.name,
        "판정 결과": final_result,
        "위험도": f"{risk_score}%",
        "신뢰도": f"{int(confidence * 100)}%",
        "분석 시간": f'{result.get("elapsed_sec", 0)}초',
        "Slice 수": "512",
        "검사 완료 시간": now.strftime("%Y-%m-%d %H:%M:%S"),
        "작업자": operator,
        "라인": selected_line,
    }

    st.session_state.ct_history.insert(0, record)

    save_inspection_report(
        battery_id=ct_id,
        inspection_type="CT 내부검사",
        result=final_result,
        risk_score=risk_score,
        operator=operator,
        line=selected_line,
        confidence=confidence,
        defect_summary=defect_summary,
        recommendation="정밀 재검사 필요" if abnormal else "정상 판정. 다음 공정 진행 가능",
        model_version="DeepLabV3Plus-MobileNet",
        overlay_path=overlay_path,
    )


def render_ct_viewer(uploaded_file):
    image_src = None

    if st.session_state.ct_analysis_done and st.session_state.latest_ct_result:
        overlay_rel_path = st.session_state.latest_ct_result.get("files", {}).get("overlay")
        if overlay_rel_path:
            overlay_path = DEEPLAB_DIR / overlay_rel_path
            image_src = file_path_to_base64(overlay_path)

    if image_src is None:
        image_src = uploaded_file_to_base64(uploaded_file)

    if image_src:
        defect_points = ""
        slice_arc = ""

        if st.session_state.ct_analysis_done:
            slice_arc = '<div class="slice-arc"></div>'
            defect_points = """
            <div class="defect-point point1"></div>
            <div class="defect-point point2"></div>
            <div class="defect-point point3"></div>
            """

        thumbnails = ""
        for slice_no in range(112, 119):
            active_class = "active" if slice_no == 114 else ""
            thumbnails += f"""
            <div class="thumb {active_class}">
                <img src="{image_src}" />
            </div>
            """

        html(f"""
        <div class="viewer-card">
            <img class="viewer-img" src="{image_src}" />
            <div class="zoom-box">
                <span>−</span> <span>|</span> <span>100%</span> <span>＋</span> <span>|</span> <span>⛶</span>
            </div>
            {slice_arc}
            {defect_points}
            <div class="arrow-left">‹</div>
            <div class="thumbnail-row">{thumbnails}</div>
            <div class="arrow-right">›</div>
        </div>
        """)
        return

    if uploaded_file is not None:
        html(f"""
        <div class="viewer-card">
            <div class="zoom-box">
                <span>−</span> <span>|</span> <span>100%</span> <span>＋</span> <span>|</span> <span>⛶</span>
            </div>
            <div class="viewer-placeholder">
                CT 파일이 업로드되었습니다: {uploaded_file.name}<br>
                이미지 미리보기는 JPG, PNG 파일에서 지원됩니다.
            </div>
        </div>
        """)
        return

    html("""
    <div class="viewer-card">
        <div class="zoom-box">
            <span>−</span> <span>|</span> <span>100%</span> <span>＋</span> <span>|</span> <span>⛶</span>
        </div>
        <div class="viewer-placeholder">
            CT Battery Image Preview
        </div>
    </div>
    """)


def render_result_content():
    if st.session_state.ct_analysis_done and st.session_state.latest_ct_result:
        latest = st.session_state.latest_ct_result or {}
        judgement = latest.get("judgement", {})

        defect_types = judgement.get("defect_types", [])
        defect_ratios = judgement.get("defect_ratios", {})
        abnormal = bool(judgement.get("abnormal", len(defect_types) > 0))

        final_result = "불량" if abnormal else "정상"
        result_class = "fail-text" if abnormal else "success-text"
        confidence = 0.94 if abnormal else 0.85
        confidence_percent = int(confidence * 100)

        defect_label_map = {
            "porosity": "기공 결함",
            "resin_overflow": "레진 오버플로우",
            "resin overflow": "레진 오버플로우",
            "swelling": "스웰링",
        }

        if defect_types:
            defect_reason_html = ""

            for defect in defect_types:
                ratio = defect_ratios.get(defect, 0)
                defect_label = defect_label_map.get(defect, defect)

                defect_reason_html += (
                    f'<span class="reason-alert">△</span> '
                    f'{defect_label} 감지 '
                    f'<span style="color:#64748B;">({defect}: {ratio}%)</span><br>'
                )
        else:
            defect_reason_html = '<span style="color:#16A34A;">✓</span> 주요 결함 없음<br>'

        risk_score = int(round(sum(float(v) for v in defect_ratios.values())))
        risk_score = min(max(risk_score, 0), 100)
        gauge_degree = int(risk_score * 1.8)

        if risk_score == 0:
            risk_level = "낮음"
            risk_class = "success-text"
        elif risk_score < 5:
            risk_level = "경미"
            risk_class = "fail-text"
        elif risk_score < 20:
            risk_level = "주의"
            risk_class = "fail-text"
        else:
            risk_level = "위험"
            risk_class = "fail-text"

        html(f"""
        <div class="result-box">
            <div class="result-line">
                <span class="result-label">판정 결과</span>
                <span class="{result_class}">{final_result}</span>
                <span class="confidence">신뢰도 {confidence_percent}%</span>
            </div>
        </div>
        <div class="result-box">
            <div class="reason-list">
                <b>{'불량 이유' if abnormal else '분석 결과'}</b><br>
                {defect_reason_html}
            </div>
        </div>
        <div class="result-box">
            <div class="result-label">위험도</div>
            <div class="{risk_class}" style="font-size:26px; margin-top:8px;">{risk_level}</div>
            <div class="gauge-wrap">
                <div class="gauge-bg" style="background: conic-gradient(from 270deg, #EF4444 0deg {gauge_degree}deg, #E5E7EB {gauge_degree}deg 180deg, transparent 180deg 360deg);"></div>
                <div class="gauge-inner"></div>
                <div class="gauge-score">{risk_score}%</div>
                <div class="gauge-left">0%</div>
                <div class="gauge-right">100%</div>
            </div>
        </div>
        <div class="result-box">
            <div style="display:grid; grid-template-columns:1fr 1.6fr; gap:8px; font-size:14px; line-height:1.8;">
                <b>검사 시간</b>
                <div>
                    분석 소요 시간&nbsp;&nbsp; <b>{latest.get("elapsed_sec", "-")}초</b><br>
                    검사 완료 시간&nbsp;&nbsp; <b>{st.session_state.get("latest_ct_completed_at", "-")}</b>
                </div>
            </div>
        </div>
        """)
    else:
        html("""
        <div class="result-box" style="height:310px; display:flex; align-items:center; justify-content:center; text-align:center;">
            <div style="color:#64748B; font-weight:800; line-height:1.7;">
                CT 파일을 업로드한 뒤<br>
                <span style="color:#0B63FF;">AI 분석 시작</span> 버튼을 눌러주세요.
            </div>
        </div>
        """)


def render_file_info(uploaded_file):
    if uploaded_file:
        file_size = round(uploaded_file.size / 1024, 2)
        html(f"""
        <div class="result-box">
            <div style="line-height:2.1; font-size:14px;">
                <b>파일명</b><br>{uploaded_file.name}<br><br>
                <b>파일 크기</b><br>{file_size} KB<br><br>
                <b>파일 타입</b><br>{uploaded_file.type or "CT/DICOM"}<br><br>
                <b>업로드 상태</b><br>업로드 완료
            </div>
        </div>
        """)
    else:
        html("""
        <div class="result-box" style="height:250px; display:flex; align-items:center; justify-content:center;">
            <div style="color:#64748B; font-weight:800;">업로드된 CT 파일이 없습니다.</div>
        </div>
        """)


def render_slice_info():
    latest = st.session_state.latest_ct_result

    if latest:
        slice_df = pd.DataFrame({
            "항목": ["Result ID", "Original Width", "Original Height", "Model Width", "Model Height"],
            "값": [
                latest.get("id", "-"),
                latest.get("original_size", {}).get("width", "-"),
                latest.get("original_size", {}).get("height", "-"),
                latest.get("model_input_size", {}).get("width", "-"),
                latest.get("model_input_size", {}).get("height", "-"),
            ],
        })
    else:
        slice_df = pd.DataFrame({
            "항목": ["Current Slice", "Total Slices", "Voxel Size", "Window Level", "Window Width"],
            "값": ["114", "512", "0.42 mm", "40 HU", "400 HU"],
        })

    st.dataframe(slice_df, use_container_width=True, hide_index=True)


def render_analysis_range():
    latest = st.session_state.latest_ct_result

    if latest:
        judgement = latest.get("judgement", {})
        defect_ratios = judgement.get("defect_ratios", {})
        all_class_ratios = judgement.get("all_class_ratios", {})

        range_df = pd.DataFrame({
            "구간": ["resin_overflow", "porosity", "battery_outline"],
            "비율": [
                f'{defect_ratios.get("resin_overflow", 0)}%',
                f'{defect_ratios.get("porosity", 0)}%',
                f'{all_class_ratios.get("battery_outline", 0)}%',
            ],
            "상태": [
                "이상" if defect_ratios.get("resin_overflow", 0) > 0 else "정상",
                "이상" if defect_ratios.get("porosity", 0) > 0 else "정상",
                "검출" if judgement.get("battery_outline_detected", False) else "미검출",
            ],
        })
    else:
        range_df = pd.DataFrame({
            "구간": ["resin_overflow", "porosity", "battery_outline"],
            "비율": ["-", "-", "-"],
            "상태": ["대기", "대기", "대기"],
        })

    st.dataframe(range_df, use_container_width=True, hide_index=True)


def render_detail_data():
    latest = st.session_state.latest_ct_result

    if latest:
        judgement = latest.get("judgement", {})

        defect_types = judgement.get("defect_types", [])
        defect_ratios = judgement.get("defect_ratios", {})
        defect_pixel_counts = judgement.get("defect_pixel_counts", {})
        all_class_pixel_counts = judgement.get("all_class_pixel_counts", {})
        all_class_ratios = judgement.get("all_class_ratios", {})

        abnormal = bool(judgement.get("abnormal", len(defect_types) > 0))
        final_result = "불량" if abnormal else "정상"

        risk_score = int(round(sum(float(v) for v in defect_ratios.values())))
        risk_score = min(max(risk_score, 0), 100)

        confidence = 0.94 if abnormal else 0.85

        model_width = latest.get("model_input_size", {}).get("width", "-")
        model_height = latest.get("model_input_size", {}).get("height", "-")
        original_width = latest.get("original_size", {}).get("width", "-")
        original_height = latest.get("original_size", {}).get("height", "-")

        defect_area_text = ", ".join(
            [f"{k}: {v}px" for k, v in defect_pixel_counts.items()]
        ) if defect_pixel_counts else "-"

        defect_ratio_text = ", ".join(
            [f"{k}: {v}%" for k, v in defect_ratios.items()]
        ) if defect_ratios else "-"

        all_class_area_text = ", ".join(
            [f"{k}: {v}px" for k, v in all_class_pixel_counts.items()]
        ) if all_class_pixel_counts else "-"

        all_class_ratio_text = ", ".join(
            [f"{k}: {v}%" for k, v in all_class_ratios.items()]
        ) if all_class_ratios else "-"

        detail_df = pd.DataFrame({
            "항목": [
                "Model",
                "Prediction",
                "Confidence",
                "Risk Score",
                "Defect Types",
                "Defect Pixel Area",
                "Defect Ratio",
                "All Class Pixel Area",
                "All Class Ratio",
                "Original Size",
                "Mask Size",
                "Elapsed",
            ],
            "값": [
                "DeepLabV3Plus-MobileNet",
                final_result,
                f"{int(confidence * 100)}%",
                f"{risk_score}%",
                ", ".join(defect_types) if defect_types else "주요 결함 없음",
                defect_area_text,
                defect_ratio_text,
                all_class_area_text,
                all_class_ratio_text,
                f"{original_width} x {original_height}",
                f"{model_width} x {model_height}",
                f'{latest.get("elapsed_sec", "-")}초',
            ],
        })
    else:
        detail_df = pd.DataFrame({
            "항목": [
                "Model",
                "Prediction",
                "Confidence",
                "Risk Score",
                "Defect Types",
                "Defect Pixel Area",
                "Defect Ratio",
                "All Class Pixel Area",
                "All Class Ratio",
                "Original Size",
                "Mask Size",
                "Elapsed",
            ],
            "값": [
                "DeepLabV3Plus-MobileNet",
                "-", "-", "-", "-", "-", "-", "-", "-", "-", "-", "-"
            ],
        })

    st.dataframe(detail_df, use_container_width=True, hide_index=True)


def render_result_panel(uploaded_file):
    tab1, tab2, tab3, tab4 = st.tabs(["분석 결과", "Slice 정보", "분석 구간", "상세 데이터"])
    with tab1: render_result_content()
    with tab2:
        render_file_info(uploaded_file)
        render_slice_info()
    with tab3: render_analysis_range()
    with tab4: render_detail_data()


def render_history_table(df):
    html("""
    <div class="section-card">
        <div class="section-head">
            <div class="section-title">최근 CT 검사 이력</div>
            <div class="link-text">전체 보기</div>
        </div>
    """)

    if df.empty:
        html("""
        <div class="empty-box">아직 저장된 CT 검사 이력이 없습니다.</div>
        </div>
        """)
        return
    html("</div>")

    st.dataframe(
        df[["CT ID", "파일명", "판정 결과", "위험도", "신뢰도", "분석 시간", "Slice 수", "검사 완료 시간", "작업자"]],
        use_container_width=True,
        hide_index=True,
    )


# ==================================================
# 👥 2. 왼쪽 고정 사이드바 조립 영역 (첫 번째 페이지 방식으로 전면 통일)
# ==================================================
with st.sidebar:
    # 로고 영역 정의
    html("""
    <div class="sidebar-logo-area">
        <div class="sidebar-title"><span class="sidebar-logo-icon"></span> CellGuard AI</div>
        <div class="sidebar-subtitle">Battery Inspection</div>
    </div>
    """)
    
    # 네비게이션 링크 
    st.page_link("pages/exterior_inspection.py", label="🔍 Exterior Inspection", use_container_width=True)
    st.page_link("pages/ct_inspection.py", label="☢ CT Inspection", use_container_width=True)
    st.page_link("pages/inspection_report.py", label="📋 Inspection Report", use_container_width=True)
    
    # 작업자 카드 정의
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M")
    current_operator = st.session_state.get("user_id", "1")
    html(f"""
    <div class="operator-card">
        <div class="operator-title">👤 Operator</div>
        <div class="operator-name">{current_operator}</div>
        <div class="operator-time">Access Time: {now_str}</div>
    </div>
    """)
    
    # 로그아웃 영역 정의
    st.markdown('<div class="logout-btn-wrap">', unsafe_allow_html=True)
    if st.button("Logout", key="btn_logout"):
        st.session_state.login = False
        st.switch_page("streamlit_app.py")
    st.markdown('</div>', unsafe_allow_html=True)


# ==================================================
# 💻 3. 메인 대시보드 화면 영역 
# ==================================================
top_left, top_right = st.columns([2.35, 1.65])
with top_left:
    html('<div class="main-title">AI 배터리 CT 내부검사</div>')
    html('<div class="sub-title">CT 이미지를 기반으로 내부 결함, 구조 이상, 위험도를 분석합니다.</div>')

with top_right:
    f1, f2, f3 = st.columns([1, 1, 1.45])
    with f1: selected_date = st.date_input("날짜", value=datetime.today(), label_visibility="collapsed")
    with f2: selected_line = st.selectbox("라인", ["전체 라인", "A Line", "B Line", "C Line"], label_visibility="collapsed")
    with f3: search_id = st.text_input("검색", placeholder="CT ID 검색", label_visibility="collapsed")

# 메트릭 대시보드
m1, m2, m3, m4 = st.columns(4)
with m1: metric_card("오늘 CT 검사 수", "1,156 건", '전일 대비 <span class="up">↑ 14.3%</span>', "▣", "icon-blue")
with m2: metric_card("정상", "842 건", "72.9%", "✓", "icon-green")
with m3: metric_card("내부 이상", "314 건", "27.1%", "△", "icon-red")
with m4: metric_card("평균 분석 시간", "2.4 분", '전일 대비 <span class="down">↓ 0.3분</span>', "◷", "icon-purple")

html("<div style='height:10px;'></div>")

# 업로드 및 메인 뷰어 그리드
main_left, main_right = st.columns([2.35, 1])
with main_left:
    html("""
    <div class="upload-box">
        <div class="upload-icon">☁</div>
        <div>
            <div class="upload-title">CT 파일 업로드</div>
            <div class="upload-desc">CT 이미지 파일 또는 폴더를 선택하세요. (DICOM, NRRD, TIFF, JPG, PNG)</div>
        </div>
    </div>
    """)

    upload_col, analyze_col = st.columns([4, 1])
    with upload_col:
        uploaded_file = st.file_uploader("파일 선택", type=["jpg", "jpeg", "png", "tif", "tiff", "dcm", "dicom", "nrrd"], label_visibility="collapsed")
    with analyze_col:
        analyze_clicked = st.button("✣ AI 분석 시작", key="ct_analyze_btn", type="primary")

    if uploaded_file is None:
        st.session_state.ct_analysis_done = False
        st.session_state.ct_saved_upload_signature = None
        st.session_state.latest_ct_result = None
        st.session_state.latest_ct_completed_at = "-"

    if analyze_clicked:
        if uploaded_file:
            try:
                upload_path = DEEPLAB_DIR / "uploads" / uploaded_file.name
                upload_path.parent.mkdir(parents=True, exist_ok=True)

                with open(upload_path, "wb") as f:
                    f.write(uploaded_file.getvalue())

                with st.spinner("DeepLab CT 분석 중..."):
                    result = predict_one_image(upload_path)

                st.session_state.ct_analysis_done = True
                st.session_state.latest_ct_result = result
                st.session_state.latest_ct_completed_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

                save_ct_record(uploaded_file, selected_line, result)

                st.success("AI 분석이 완료되었습니다. 최근 CT 검사 이력과 보고서에 저장되었습니다.")

            except Exception as e:
                st.session_state.ct_analysis_done = False
                st.session_state.latest_ct_result = None
                st.session_state.latest_ct_completed_at = "-"
                st.error(f"CT 분석 중 오류가 발생했습니다: {e}")
        else:
            st.warning("먼저 CT 파일을 업로드해주세요.")

    render_ct_viewer(uploaded_file)

with main_right:
    render_result_panel(uploaded_file)

html("<div style='height:10px;'></div>")

# 하단 히스토리 및 로그 테이블 필터링
history_df = pd.DataFrame(st.session_state.ct_history)
if history_df.empty:
    filtered_df = history_df
else:
    filtered_df = history_df.copy()
    if selected_line != "전체 라인":
        filtered_df = filtered_df[filtered_df["라인"] == selected_line]
    if search_id.strip():
        filtered_df = filtered_df[
            filtered_df["CT ID"].str.contains(search_id.strip(), case=False, na=False) | 
            filtered_df["파일명"].str.contains(search_id.strip(), case=False, na=False)
        ]

render_history_table(filtered_df)
