import base64
import textwrap
from datetime import datetime

import pandas as pd
import streamlit as st

from services.custom_vision_out import predict_exterior_custom_vision
from utils.report_storage import save_inspection_report


# =========================
# 1. Page Config & Login Check
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
# Session State Init
# =========================
if "analysis_done" not in st.session_state:
    st.session_state.analysis_done = False

if "inspection_history" not in st.session_state:
    st.session_state.inspection_history = []

if "latest_exterior_result" not in st.session_state:
    st.session_state.latest_exterior_result = None

if "latest_exterior_completed_at" not in st.session_state:
    st.session_state.latest_exterior_completed_at = "-"


# =========================
# CSS
# =========================
html("""
<style>
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

div[data-testid="collapsedControl"] { z-index: 999999 !important; }
button[data-testid="stSidebarCollapseButton"] {
    background-color: #FFFFFF !important;
    border: 1px solid #E5EAF3 !important;
    border-radius: 8px !important;
    box-shadow: 0 2px 8px rgba(15, 23, 42, 0.08) !important;
}

div[data-testid="stPageLink-FormSubmitButton"] > div,
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

.sidebar-logo-area { margin-bottom: 30px; padding-left: 8px; }
.sidebar-title { font-size: 21px; font-weight: 800; color: #0F172A; display: flex; align-items: center; gap: 10px; }
.sidebar-logo-icon { width: 20px; height: 24px; background: #3B82F6; border-radius: 4px 4px 10px 10px; display: inline-block; }
.sidebar-subtitle { font-size: 12px; font-weight: 600; color: #64748B; margin-top: 4px; padding-left: 30px; }

.operator-card { border: 1px solid #E5EAF3; border-radius: 16px; padding: 16px; background: #FFFFFF; margin-top: 40px; }
.operator-title { font-size: 13.5px; font-weight: 700; color: #475569; display: flex; align-items: center; gap: 8px; margin-bottom: 10px; }
.operator-name { font-size: 16px; font-weight: 800; color: #0F172A; margin-bottom: 16px; padding-left: 22px; }
.operator-time { font-size: 11px; color: #64748B; padding-left: 22px; font-weight: 600; }

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

.viewer-card { border-radius: 13px; overflow: hidden; border: 1px solid #1F2937; height: 420px; position: relative; box-shadow: 0 8px 22px rgba(15, 23, 42, 0.12); background: #0B0F16; }
.viewer-img { width: 100%; height: 420px; object-fit: contain; display: block; opacity: 0.98; background: #0B0F16; }
.viewer-placeholder { height: 420px; background: linear-gradient(135deg, #111827, #020617); display: flex; justify-content: center; align-items: center; color: #94A3B8; font-size: 18px; font-weight: 800; text-align: center; line-height: 1.7; }
.zoom-box { position: absolute; top: 16px; left: 16px; background: rgba(15, 23, 42, 0.82); color: #FFFFFF; border: 1px solid rgba(255,255,255,0.12); border-radius: 8px; padding: 9px 14px; font-size: 14px; font-weight: 800; display: flex; gap: 13px; align-items: center; z-index: 3; }

div[data-testid="stTabs"] { background: #FFFFFF; border: 1px solid #E4EAF3; border-radius: 16px; padding: 20px 18px; min-height: 420px; box-shadow: 0 8px 22px rgba(15, 23, 42, 0.05); }
div[data-testid="stTabs"] button { font-weight: 900 !important; color: #475569 !important; }

.result-box { border: 1px solid #E4EAF3; border-radius: 10px; padding: 14px 14px; margin-bottom: 10px; background: #FFFFFF; }
.result-line { display: flex; justify-content: space-between; align-items: center; }
.result-label { font-size: 14px; font-weight: 850; color: #334155; }
.fail-text { color: #EF1C1C; font-size: 28px; font-weight: 950; }
.success-text { color: #16A34A; font-size: 28px; font-weight: 950; }
.warning-text { color: #F97316; font-size: 28px; font-weight: 950; }
.confidence { color: #0B63FF; font-size: 16px; font-weight: 950; }
.reason-list { font-size: 14px; line-height: 2.0; font-weight: 700; color: #1F2937; }
.reason-alert { color: #EF4444; margin-right: 6px; }

.gauge-wrap { position: relative; height: 112px; margin-top: 6px; }
.gauge-bg { position: absolute; width: 190px; height: 95px; left: 50%; top: 8px; transform: translateX(-50%); border-radius: 190px 190px 0 0; }
.gauge-inner { position: absolute; width: 132px; height: 66px; left: 50%; top: 37px; transform: translateX(-50%); border-radius: 132px 132px 0 0; background: #FFFFFF; }
.gauge-score { position: absolute; top: 54px; left: 0; right: 0; text-align: center; font-size: 34px; font-weight: 950; color: #0F172A; }
.gauge-left { position: absolute; left: 28%; bottom: 6px; font-size: 12px; font-weight: 800; color: #334155; }
.gauge-right { position: absolute; right: 20%; bottom: 6px; font-size: 12px; font-weight: 800; color: #334155; }

.section-card { background: #FFFFFF; border: 1px solid #E4EAF3; border-radius: 16px; padding: 18px; box-shadow: 0 8px 22px rgba(15, 23, 42, 0.05); }
.section-head { display: flex; justify-content: space-between; align-items: center; margin-bottom: 14px; }
.section-title { font-size: 17px; font-weight: 950; color: #0F172A; }
.link-text { font-size: 13px; color: #0B63FF; font-weight: 900; }
.empty-box { height: 140px; border: 1px dashed #CBD5E1; border-radius: 12px; display: flex; align-items: center; justify-content: center; color: #64748B; font-size: 14px; font-weight: 800; background: #FBFDFF; }
</style>
""")


# =========================
# Utility Functions
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
    mime_type = uploaded_file.type or "image/png"
    encoded = base64.b64encode(uploaded_file.getvalue()).decode("utf-8")
    return f"data:{mime_type};base64,{encoded}"


def normalize_custom_vision_result(raw_result):
    predictions = raw_result.get("predictions", [])

    if not predictions:
        return {
            "label": "Unknown",
            "confidence": 0.0,
            "confidence_percent": 0.0,
            "result": "확인 필요",
            "risk_score": 0,
            "risk_level": "낮음",
            "defect_summary": "예측 결과가 없습니다.",
            "recommendation": "이미지 또는 모델 연결 상태를 확인하세요.",
            "top_predictions": [],
        }

    sorted_predictions = sorted(predictions, key=lambda x: x.get("probability", 0), reverse=True)
    top = sorted_predictions[0]

    label = top.get("tagName", "Unknown")
    confidence = float(top.get("probability", 0))
    confidence_percent = round(confidence * 100, 2)

    label_lower = label.lower()
    normal_keywords = ["normal", "정상", "good", "ok"]
    is_normal = any(keyword in label_lower for keyword in normal_keywords)

    result = "정상" if is_normal else "불량"
    risk_score = max(0, min(100, int(round(confidence_percent if not is_normal else 100 - confidence_percent))))

    if risk_score == 0:
        risk_level = "낮음"
    elif risk_score < 5:
        risk_level = "경미"
    elif risk_score < 20:
        risk_level = "주의"
    else:
        risk_level = "위험"

    defect_label_map = {
        "normal": "정상",
        "damaged": "외관 손상",
        "damage": "외관 손상",
        "pollution": "오염",
        "swelling": "스웰링",
        "scratch": "스크래치",
        "dent": "찌그러짐",
    }
    display_label = defect_label_map.get(label_lower, label)

    if is_normal:
        defect_summary = "외관상 주요 결함이 감지되지 않았습니다."
        recommendation = "정상 판정. 다음 공정 진행 가능"
    else:
        defect_summary = f"{display_label} 가능성 감지"
        recommendation = "정밀 재검사 필요"

    top_predictions = [
        {
            "label": pred.get("tagName", "Unknown"),
            "probability": round(float(pred.get("probability", 0)) * 100, 2),
        }
        for pred in sorted_predictions[:5]
    ]

    return {
        "label": label,
        "display_label": display_label,
        "confidence": confidence,
        "confidence_percent": confidence_percent,
        "result": result,
        "risk_score": risk_score,
        "risk_level": risk_level,
        "defect_summary": defect_summary,
        "recommendation": recommendation,
        "top_predictions": top_predictions,
    }


def save_exterior_record(uploaded_file, selected_line, parsed):
    now = datetime.now()
    battery_id = f"B-{len(st.session_state.inspection_history) + 1:03d}"
    operator_id = str(st.session_state.get("user_id", "1"))

    record = {
        "배터리 ID": battery_id,
        "파일명": uploaded_file.name,
        "판정 결과": parsed["result"],
        "예측 라벨": parsed.get("display_label", parsed["label"]),
        "위험도": f'{parsed["risk_score"]}%',
        "신뢰도": f'{parsed["confidence_percent"]}%',
        "검사 완료 시간": now.strftime("%Y-%m-%d %H:%M:%S"),
        "작업자": operator_id,
        "라인": selected_line,
    }

    st.session_state.inspection_history.insert(0, record)

    save_inspection_report(
        battery_id=battery_id,
        inspection_type="외관 검사",
        result=parsed["result"],
        risk_score=parsed["risk_score"],
        operator=operator_id,
        line=selected_line,
        confidence=parsed["confidence"],
        defect_summary=parsed["defect_summary"],
        recommendation=parsed["recommendation"],
        model_version="Custom Vision - battery_out",
    )

    return battery_id


def render_exterior_viewer(uploaded_file):
    image_src = uploaded_file_to_base64(uploaded_file)

    if image_src:
        html(f"""
        <div class="viewer-card">
            <img class="viewer-img" src="{image_src}" />
            <div class="zoom-box">
                <span>100%</span>
            </div>
        </div>
        """)
        return

    html("""
    <div class="viewer-card">
        <div class="zoom-box">
            <span>100%</span>
        </div>
        <div class="viewer-placeholder">
            Battery Exterior Image Preview
        </div>
    </div>
    """)


def render_result_content():
    latest = st.session_state.latest_exterior_result

    if st.session_state.analysis_done and latest:
        parsed = latest["parsed"]

        result_class = "success-text" if parsed["result"] == "정상" else "fail-text"
        risk_score = parsed["risk_score"]
        gauge_degree = int(risk_score * 1.8)

        if risk_score == 0:
            risk_class = "success-text"
        elif risk_score < 5:
            risk_class = "warning-text"
        elif risk_score < 20:
            risk_class = "warning-text"
        else:
            risk_class = "fail-text"

        if parsed["result"] == "정상":
            reason_title = "분석 결과"
            reason_html = '<span style="color:#16A34A;">✓</span> 주요 외관 결함 없음<br>'
        else:
            reason_title = "불량 이유"
            reason_html = f'<span class="reason-alert">△</span> {parsed["defect_summary"]}<br>'

        html(f"""
        <div class="result-box">
            <div class="result-line">
                <span class="result-label">판정 결과</span>
                <span class="{result_class}">{parsed["result"]}</span>
                <span class="confidence">신뢰도 {parsed["confidence_percent"]}%</span>
            </div>
        </div>
        <div class="result-box">
            <div class="reason-list">
                <b>{reason_title}</b><br>
                {reason_html}
            </div>
        </div>
        <div class="result-box">
            <div class="result-label">위험도</div>
            <div class="{risk_class}" style="font-size:26px; margin-top:8px;">{parsed["risk_level"]}</div>
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
                    분석 방식&nbsp;&nbsp; <b>Custom Vision</b><br>
                    검사 완료 시간&nbsp;&nbsp; <b>{st.session_state.get("latest_exterior_completed_at", "-")}</b>
                </div>
            </div>
        </div>
        """)
    else:
        html("""
        <div class="result-box" style="height:310px; display:flex; align-items:center; justify-content:center; text-align:center;">
            <div style="color:#64748B; font-weight:800; line-height:1.7;">
                외관 이미지를 업로드한 뒤<br>
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
                <b>파일 타입</b><br>{uploaded_file.type or "image"}<br><br>
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
    latest = st.session_state.latest_exterior_result

    if latest:
        parsed = latest["parsed"]
        raw = latest["raw"]
        predictions = parsed.get("top_predictions", [])

        prediction_text = ", ".join([f'{p["label"]}: {p["probability"]}%' for p in predictions]) if predictions else "-"

        detail_df = pd.DataFrame({
            "항목": [
                "Model",
                "Prediction",
                "Top Label",
                "Confidence",
                "Risk Score",
                "Risk Level",
                "Recommendation",
                "Top Predictions",
                "Result Source",
            ],
            "값": [
                "Custom Vision - battery_out",
                parsed["result"],
                parsed.get("display_label", parsed["label"]),
                f'{parsed["confidence_percent"]}%',
                f'{parsed["risk_score"]}%',
                parsed["risk_level"],
                parsed["recommendation"],
                prediction_text,
                "Azure Custom Vision API",
            ],
        })
    else:
        detail_df = pd.DataFrame({
            "항목": ["Model", "Prediction", "Top Label", "Confidence", "Risk Score", "Risk Level", "Recommendation", "Top Predictions", "Result Source"],
            "값": ["Custom Vision - battery_out", "-", "-", "-", "-", "-", "-", "-", "Azure Custom Vision API"],
        })

    st.dataframe(detail_df, use_container_width=True, hide_index=True)

    if latest:
        with st.expander("Custom Vision 원본 JSON 보기"):
            st.json(latest["raw"])


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
            <div class="section-title">최근 외관 검사 이력</div>
            <div class="link-text">전체 보기</div>
        </div>
    """)

    if df.empty:
        html("""
        <div class="empty-box">아직 저장된 외관 검사 이력이 없습니다.</div>
        </div>
        """)
        return

    html("</div>")
    st.dataframe(df, use_container_width=True, hide_index=True)


# =========================
# Sidebar
# =========================
with st.sidebar:
    html("""
    <div class="sidebar-logo-area">
        <div class="sidebar-title"><span class="sidebar-logo-icon"></span> CellGuard AI</div>
        <div class="sidebar-subtitle">Battery Inspection</div>
    </div>
    """)

    st.page_link("pages/exterior_inspection.py", label="🔍 Exterior Inspection", use_container_width=True)
    st.page_link("pages/ct_inspection.py", label="☢ CT Inspection", use_container_width=True)
    st.page_link("pages/inspection_report.py", label="📋 Inspection Report", use_container_width=True)

    now_str = datetime.now().strftime("%Y-%m-%d %H:%M")
    current_operator = st.session_state.get("user_id", "1")

    html(f"""
    <div class="operator-card">
        <div class="operator-title">👤 Operator</div>
        <div class="operator-name">{current_operator}</div>
        <div class="operator-time">Access Time: {now_str}</div>
    </div>
    """)

    st.markdown('<div class="logout-btn-wrap">', unsafe_allow_html=True)
    if st.button("Logout", key="btn_logout"):
        st.session_state.login = False
        st.switch_page("streamlit_app.py")
    st.markdown("</div>", unsafe_allow_html=True)


# =========================
# Main Page
# =========================
top_left, top_right = st.columns([2.35, 1.65])
with top_left:
    html('<div class="main-title">AI 배터리 외관 검사</div>')
    html('<div class="sub-title">배터리 외관 이미지를 업로드하여 Custom Vision 기반 정밀 분석을 수행합니다.</div>')

with top_right:
    f1, f2, f3 = st.columns([1, 1, 1.45])
    with f1:
        selected_date = st.date_input("날짜", value=datetime.today(), label_visibility="collapsed")
    with f2:
        selected_line = st.selectbox("라인", ["전체 라인", "A Line", "B Line", "C Line"], label_visibility="collapsed")
    with f3:
        search_id = st.text_input("검색", placeholder="배터리 ID 검색", label_visibility="collapsed")

# Demo KPI cards. 우측 분석 결과/하단 이력은 실제 Custom Vision 결과 기반.
m1, m2, m3, m4 = st.columns(4)
with m1:
    metric_card("전체 검사", "1,248 건", '전일 대비 <span class="up">↑ 12.5%</span>', "▣", "icon-blue")
with m2:
    metric_card("정상", "982 건", "78.8%", "✓", "icon-green")
with m3:
    metric_card("불량", "266 건", "21.2%", "△", "icon-red")
with m4:
    metric_card("평균 분석 시간", "1.8 초", '전일 대비 <span class="down">↓ 0.2초</span>', "◷", "icon-purple")

html("<div style='height:10px;'></div>")

main_left, main_right = st.columns([2.35, 1])

with main_left:
    html("""
    <div class="upload-box">
        <div class="upload-icon">☁</div>
        <div>
            <div class="upload-title">이미지 업로드</div>
            <div class="upload-desc">외관 검사 이미지를 선택하세요. (JPG, PNG)</div>
        </div>
    </div>
    """)

    upload_col, analyze_col = st.columns([4, 1])
    with upload_col:
        uploaded_file = st.file_uploader("파일 선택", type=["jpg", "jpeg", "png"], label_visibility="collapsed")
    with analyze_col:
        analyze_clicked = st.button("✣ AI 분석 시작", key="exterior_analyze_btn", type="primary")

    if uploaded_file is None:
        st.session_state.analysis_done = False
        st.session_state.latest_exterior_result = None
        st.session_state.latest_exterior_completed_at = "-"

    if analyze_clicked:
        if uploaded_file:
            try:
                image_bytes = uploaded_file.getvalue()

                with st.spinner("Custom Vision 외관 분석 중..."):
                    raw_result = predict_exterior_custom_vision(image_bytes)

                parsed = normalize_custom_vision_result(raw_result)

                st.session_state.analysis_done = True
                st.session_state.latest_exterior_result = {
                    "raw": raw_result,
                    "parsed": parsed,
                }
                st.session_state.latest_exterior_completed_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

                battery_id = save_exterior_record(uploaded_file, selected_line, parsed)
                st.success(f"배터리 {battery_id} 분석 완료 및 보고서 저장 완료")

            except Exception as e:
                st.session_state.analysis_done = False
                st.session_state.latest_exterior_result = None
                st.session_state.latest_exterior_completed_at = "-"
                st.error(f"Custom Vision 분석 중 오류가 발생했습니다: {e}")
        else:
            st.warning("먼저 외관 이미지를 업로드해주세요.")

    render_exterior_viewer(uploaded_file)

with main_right:
    render_result_panel(uploaded_file)

html("<div style='height:10px;'></div>")

history_df = pd.DataFrame(st.session_state.inspection_history)
if history_df.empty:
    filtered_df = history_df
else:
    filtered_df = history_df.copy()
    if selected_line != "전체 라인" and "라인" in filtered_df.columns:
        filtered_df = filtered_df[filtered_df["라인"] == selected_line]
    if search_id.strip():
        filtered_df = filtered_df[
            filtered_df["배터리 ID"].astype(str).str.contains(search_id.strip(), case=False, na=False)
            | filtered_df["파일명"].astype(str).str.contains(search_id.strip(), case=False, na=False)
        ]

render_history_table(filtered_df)
