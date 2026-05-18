import base64
import textwrap
import io
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
# CSS (이전 코드의 모든 스타일 복구)
# =========================
html("""
<style>
.stApp { background: #F8FBFF; color: #111827; }
header[data-testid="stHeader"] { background-color: rgba(0,0,0,0) !important; color: #475569 !important; }
footer, #MainMenu { visibility: hidden; }

.block-container { padding-top: 1.6rem; padding-left: 2.4rem; padding-right: 2.4rem; padding-bottom: 2rem; max-width: 100%; }
section[data-testid="stSidebar"] { background: #FFFFFF; border-right: 1px solid #E5EAF3; }

div[data-testid="stVerticalBlock"] { gap: 0.65rem; }
label { font-size: 13px !important; color: #334155 !important; font-weight: 700 !important; }
div[data-baseweb="input"] input { font-size: 14px !important; }

.stButton > button {
    width: 100%; height: 44px; border-radius: 10px; border: 1px solid #D7E1F2;
    background: #FFFFFF; color: #111827; font-weight: 800; font-size: 14px;
}
.stButton > button:hover { border-color: #0B63FF; color: #0B63FF; }
div[data-testid="stButton"] button[kind="primary"] { background: #0B63FF !important; color: white !important; border: 1px solid #0B63FF !important; }

.main-title { font-size: 34px; font-weight: 950; color: #0F172A; margin-bottom: 6px; letter-spacing: -0.8px; }
.sub-title { font-size: 15px; color: #475569; margin-bottom: 20px; }

.metric-card {
    height: 116px; background: #FFFFFF; border: 1px solid #E4EAF3; border-radius: 16px;
    padding: 19px 21px; box-shadow: 0 8px 22px rgba(15, 23, 42, 0.05); display: flex; align-items: center; gap: 18px;
}
.metric-icon { width: 58px; height: 58px; border-radius: 50%; display: flex; justify-content: center; align-items: center; font-size: 27px; font-weight: 900; }
.icon-blue { background: #EAF2FF; color: #0B63FF; }
.icon-green { background: #DCFCE7; color: #16A34A; }
.icon-red { background: #FEE2E2; color: #EF4444; }
.icon-purple { background: #F3E8FF; color: #7E22CE; }

.metric-label { font-size: 14px; font-weight: 800; color: #334155; margin-bottom: 4px; }
.metric-value { font-size: 28px; font-weight: 950; color: #0F172A; line-height: 1.1; }
.metric-sub { font-size: 14px; color: #64748B; margin-top: 7px; }
.up { color: #0B63FF; font-weight: 900; }
.down { color: #EF4444; font-weight: 900; }

.upload-box { border: 1.5px dashed #9FC2FF; border-radius: 15px; background: #FBFDFF; padding: 18px 20px; display: flex; align-items: center; gap: 16px; margin-bottom: 10px; }
.upload-icon { font-size: 36px; color: #0B63FF; }
.upload-title { font-size: 18px; font-weight: 950; color: #0F172A; }
.upload-desc { font-size: 14px; color: #64748B; margin-top: 4px; }

.viewer-card { background: #0B0F16; border-radius: 13px; overflow: hidden; border: 1px solid #1F2937; height: 420px; position: relative; box-shadow: 0 8px 22px rgba(15, 23, 42, 0.12); }
.viewer-img { width: 100%; height: 420px; object-fit: cover; display: block; opacity: 0.96; }
.viewer-placeholder { height: 420px; background: linear-gradient(135deg, #111827, #020617); display: flex; justify-content: center; align-items: center; color: #94A3B8; font-size: 18px; font-weight: 800; }

.zoom-box { position: absolute; top: 16px; left: 16px; background: rgba(15, 23, 42, 0.82); color: #FFFFFF; border: 1px solid rgba(255,255,255,0.12); border-radius: 8px; padding: 9px 14px; font-size: 14px; font-weight: 800; display: flex; gap: 13px; align-items: center; z-index: 3; }

.defect-point { position: absolute; width: 25px; height: 25px; border: 3px solid #FF3B3B; border-radius: 50%; background: rgba(255, 59, 59, 0.18); box-shadow: 0 0 0 4px rgba(255, 59, 59, 0.18); z-index: 3; }
.point1 { top: 29%; left: 54%; }
.point2 { top: 49%; left: 61%; }
.point3 { top: 62%; left: 62%; }

.thumbnail-row { position: absolute; left: 145px; right: 72px; bottom: 16px; display: flex; gap: 8px; align-items: center; z-index: 3; }
.thumb { width: 104px; height: 47px; border-radius: 7px; border: 1px solid rgba(255,255,255,0.18); background: rgba(255,255,255,0.08); overflow: hidden; }
.thumb.active { border: 2px solid #0B93FF; }
.thumb img { width: 100%; height: 100%; object-fit: cover; }

.arrow-left, .arrow-right { position: absolute; bottom: 18px; width: 44px; height: 44px; background: rgba(15, 23, 42, 0.75); color: white; border-radius: 9px; display: flex; align-items: center; justify-content: center; font-size: 22px; z-index: 3; }
.arrow-left { left: 96px; } .arrow-right { right: 42px; }

div[data-testid="stTabs"] { background: #FFFFFF; border: 1px solid #E4EAF3; border-radius: 16px; padding: 20px 18px; min-height: 420px; box-shadow: 0 8px 22px rgba(15, 23, 42, 0.05); }
.result-box { border: 1px solid #E4EAF3; border-radius: 10px; padding: 14px; margin-bottom: 10px; background: #FFFFFF; }

.gauge-wrap { position: relative; height: 112px; margin-top: 6px; }
.gauge-score { position: absolute; top: 54px; left: 0; right: 0; text-align: center; font-size: 34px; font-weight: 950; color: #0F172A; }

.section-card { background: #FFFFFF; border: 1px solid #E4EAF3; border-radius: 16px; padding: 18px; box-shadow: 0 8px 22px rgba(15, 23, 42, 0.05); }
.section-head { display: flex; justify-content: space-between; align-items: center; margin-bottom: 14px; }
.section-title { font-size: 17px; font-weight: 950; color: #0F172A; }
.log-table-head { font-size: 13px; color: #64748B; font-weight: 900; padding: 8px 0; border-bottom: 1px solid #E5EAF3; }
.log-cell { font-size: 14px; color: #334155; font-weight: 800; padding: 8px 0; }
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
    if uploaded_file is None: return None
    file_bytes = uploaded_file.getvalue()
    encoded = base64.b64encode(file_bytes).decode("utf-8")
    return f"data:{uploaded_file.type or 'image/png'};base64,{encoded}"


def save_inspection_record(uploaded_file, selected_line):
    now = datetime.now()
    battery_id = f"B-{len(st.session_state.inspection_history) + 1:03d}"
    file_signature = f"{uploaded_file.name}-{uploaded_file.size}"

    if st.session_state.saved_upload_signature == file_signature: return
    st.session_state.saved_upload_signature = file_signature

    operator = st.session_state.get("user_id", "Guest")
    risk_score = 82 # 시연 데이터
    
    record = {
        "배터리 ID": battery_id, "파일명": uploaded_file.name, "판정 결과": "불량",
        "위험도": risk_score, "신뢰도": "92%", "검사 완료 시간": now.strftime("%Y-%m-%d %H:%M:%S"),
        "작업자": operator, "라인": selected_line,
    }
    log = {
        "시간": now.strftime("%H:%M"), "내용": f"{battery_id} 검사 완료",
        "판정 결과": "불량", "신뢰도": "92%", "작업자": operator,
    }

    st.session_state.inspection_history.insert(0, record)
    st.session_state.activity_logs.insert(0, log)

    save_inspection_report(
        battery_id=battery_id, inspection_type="외관 검사", result="불량",
        risk_score=risk_score, operator=operator, line=selected_line, confidence=92,
        defect_summary="Swelling 의심, 표면 찌그러짐 감지", recommendation="교체 권장", model_version="v1"
    )


def render_viewer(uploaded_file):
    image_src = uploaded_file_to_base64(uploaded_file)
    if image_src:
        defect_points = '<div class="defect-point point1"></div><div class="defect-point point2"></div><div class="defect-point point3"></div>' if st.session_state.analysis_done else ""
        thumbnails = "".join([f'<div class="thumb {"active" if i==1 else ""}"><img src="{image_src}" /></div>' for i in range(6)])
        html(f"""
        <div class="viewer-card">
            <img class="viewer-img" src="{image_src}" />
            <div class="zoom-box"><span>−</span><span>|</span><span>100%</span><span>＋</span><span>|</span><span>⛶</span></div>
            {defect_points}
            <div class="arrow-left">‹</div>
            <div class="thumbnail-row">{thumbnails}</div>
            <div class="arrow-right">›</div>
        </div>
        """)
    else:
        html('<div class="viewer-card"><div class="viewer-placeholder">Battery Preview</div></div>')


def render_result_content():
    if st.session_state.analysis_done:
        risk_val = 82
        # 강조 색상 로직 적용
        risk_color = "#EF4444" if risk_val >= 80 else "#F59E0B" if risk_val >= 50 else "#10B981"
        risk_text = "위험(즉각조치)" if risk_val >= 80 else "주의" if risk_val >= 50 else "안전"

        html(f"""
        <div class="result-box">
            <div style="display:flex; justify-content:space-between; align-items:center;">
                <span style="font-weight:800; color:#64748B;">판정 결과</span>
                <span style="color:#EF1C1C; font-size:28px; font-weight:950;">불량</span>
                <span style="color:#0B63FF; font-size:16px; font-weight:950;">신뢰도 92%</span>
            </div>
        </div>
        <div class="result-box">
            <div style="font-weight:900; color:{risk_color}; margin-bottom:10px; font-size:16px;">위험도: {risk_text}</div>
            <div class="gauge-wrap">
                <div style="position:absolute; width:190px; height:95px; left:50%; top:8px; transform:translateX(-50%); border-radius:190px 190px 0 0; background:conic-gradient(from 270deg, {risk_color} 0deg {risk_val*1.8}deg, #E5E7EB {risk_val*1.8}deg 180deg, transparent 180deg 360deg);"></div>
                <div style="position:absolute; width:132px; height:66px; left:50%; top:37px; transform:translateX(-50%); border-radius:132px 132px 0 0; background:#FFFFFF;"></div>
                <div class="gauge-score">{risk_val}%</div>
            </div>
        </div>
        <div class="result-box">
            <div style="font-size:14px; line-height:1.8;">
                <b>불량 사유</b><br>△ Swelling 의심<br>△ 표면 찌그러짐 감지<br>△ 배터리 외벽 손상
            </div>
        </div>
        """)
    else:
        html('<div class="result-box" style="height:310px; display:flex; align-items:center; justify-content:center; text-align:center;"><div style="color:#64748B; font-weight:800; line-height:1.7;">이미지를 업로드한 뒤<br><span style="color:#0B63FF;">AI 분석 시작</span> 버튼을 눌러주세요.</div></div>')


def render_history_table(df):
    html('<div class="section-card"><div class="section-head"><div class="section-title">최근 검사 이력</div></div>')
    if df.empty:
        html('<div style="height:140px; border:1px dashed #CBD5E1; border-radius:12px; display:flex; align-items:center; justify-content:center; color:#64748B; font-size:14px; font-weight:800; background:#FBFDFF;">데이터가 없습니다.</div></div>')
    else:
        html("</div>")
        st.dataframe(
            df[["배터리 ID", "파일명", "판정 결과", "위험도", "신뢰도", "검사 완료 시간", "작업자"]],
            use_container_width=True, hide_index=True,
            column_config={
                "위험도": st.column_config.ProgressColumn("위험도", format="%d%%", min_value=0, max_value=100)
            }
        )


def render_log_box():
    html('<div class="section-card"><div class="section-head"><div class="section-title">활동 로그</div></div>')
    if not st.session_state.activity_logs:
        html('<div style="height:140px; border:1px dashed #CBD5E1; border-radius:12px; display:flex; align-items:center; justify-content:center; color:#64748B; font-size:14px; font-weight:800; background:#FBFDFF;">로그가 없습니다.</div></div>')
    else:
        html("</div>")
        h1, h2, h3 = st.columns([1, 2.5, 1])
        for col, title in zip([h1, h2, h3], ["시간", "내용", "판정"]):
            with col: html(f'<div class="log-table-head">{title}</div>')
        for log in st.session_state.activity_logs[:5]:
            c1, c2, c3 = st.columns([1, 2.5, 1])
            with c1: html(f'<div class="log-cell">{log["시간"]}</div>')
            with c2: html(f'<div class="log-cell">{log["내용"]}</div>')
            with c3: st.error("불량") if log["판정 결과"] == "불량" else st.success("정상")


# =========================
# Sidebar & Header
# =========================
render_sidebar("exterior")

top_left, top_right = st.columns([2.35, 1.65])
with top_left:
    html('<div class="main-title">AI 배터리 외관 검사</div>')
    html('<div class="sub-title">배터리 외관 이미지를 업로드하여 정밀 분석을 수행합니다.</div>')

with top_right:
    f1, f2, f3 = st.columns([1, 1, 1.45])
    with f1: st.date_input("날짜", value=datetime.today(), label_visibility="collapsed")
    with f2: selected_line = st.selectbox("라인", ["전체 라인", "A Line", "B Line", "C Line"], label_visibility="collapsed")
    with f3: search_id = st.text_input("검색", placeholder="배터리 ID 검색", label_visibility="collapsed")


# =========================
# Main Display
# =========================
# Metrics
m1, m2, m3, m4 = st.columns(4)
with m1: metric_card("전체 검사", "1,248 건", '↑ 12.5%', "▣", "icon-blue")
with m2: metric_card("정상", "982 건", "78.8%", "✓", "icon-green")
with m3: metric_card("불량", "266 건", "21.2%", "△", "icon-red")
with m4: metric_card("평균 시간", "1.8 초", '↓ 0.2초', "◷", "icon-purple")

html("<div style='height:15px;'></div>")

# 분석 영역
col_main, col_res = st.columns([2.35, 1])
with col_main:
    html('<div class="upload-box"><div class="upload-icon">☁</div><div class="upload-title">이미지 업로드</div></div>')
    u_col, a_col = st.columns([4, 1])
    with u_col: uploaded_file = st.file_uploader("파일", type=["jpg", "png"], label_visibility="collapsed")
    with a_col:
        if st.button("✣ AI 분석 시작", type="primary"):
            if uploaded_file:
                st.session_state.analysis_done = True
                save_inspection_record(uploaded_file, selected_line)
    render_viewer(uploaded_file)

with col_res:
    tabs = st.tabs(["분석 결과", "이미지 정보", "상세 데이터"])
    with tabs[0]: render_result_content()
    with tabs[1]:
        if uploaded_file: html(f'<div class="result-box">파일명: {uploaded_file.name}</div>')
    with tabs[2]:
        st.write("모델 버전: v1.0.4")
        st.write("센서 ID: VS-2024-X")

# 실시간 차트 추가 (이전 코드 구성 유지)
with st.expander("📊 실시간 분석 통계", expanded=True):
    c1, c2 = st.columns(2)
    with c1: st.line_chart(pd.DataFrame({'검사수': [100, 150, 120, 200, 180]}, index=[f'{i}시' for i in range(9, 14)]))
    with c2: st.bar_chart(pd.DataFrame({'불량': [10, 25, 15, 30, 20]}, index=['A', 'B', 'C', 'D', 'E']))

html("<div style='height:20px;'></div>")

# 하단 테이블
hist_df = pd.DataFrame(st.session_state.inspection_history)
if not hist_df.empty and selected_line != "전체 라인":
    hist_df = hist_df[hist_df["라인"] == selected_line]

bl, br = st.columns([1, 1])
with bl: render_history_table(hist_df)
with br: render_log_box()