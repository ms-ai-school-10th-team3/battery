import base64
import textwrap
import io
from datetime import datetime

import pandas as pd
import streamlit as st
from utils.report_storage import save_inspection_report


# =========================
# 1. Page Config & Session Check
# =========================
st.set_page_config(
    page_title="Exterior Inspection",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded", # 순정 사이드바 사용
)

# 로그인 세션 안전하게 검증
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

if "activity_logs" not in st.session_state:
    st.session_state.activity_logs = []

if "saved_upload_signature" not in st.session_state:
    st.session_state.saved_upload_signature = None


# =========================
# 🎨 CSS 주입 (순정 사이드바를 이미지 스타일로 완벽 개조)
# =========================
html("""
<style>
/* 기본 앱 배경 설정 */
.stApp { background: #F8FBFF; color: #111827; }
header[data-testid="stHeader"] { background-color: rgba(0,0,0,0) !important; }
footer, #MainMenu { visibility: hidden; }

/* 🌟 순정 사이드바 배경 및 테두리 완전히 플랫하게 리스타일링 */
[data-testid="stSidebar"] {
    background-color: #FFFFFF !important;
    border-right: 1px solid #E5EAF3 !important;
}
[data-testid="stSidebarUserContent"] {
    padding-top: 2rem !important;
    padding-left: 1rem !important;
    padding-right: 1rem !important;
}

/* 🌟 [핵심] 순정 st.page_link의 흰색 테두리 상자 조각들을 완전히 제거 */
div[data-testid="stPageLink-FormSubmitButton"] > div,
div[data-testid="stSidebarUserContent"] div.stPageLink,
div[data-testid="stSidebarUserContent"] div.stPageLink a {
    background: transparent !important;
    background-color: transparent !important;
    border: none !important;
    box-shadow: none !important;
    text-decoration: none !important;
}

/* 🌟 메뉴 아이템 호버 및 액티브 스타일 직접 교정 */
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

/* 本문 메인 디자인 코드 상속 */
.main-title { font-size: 34px; font-weight: 950; color: #0F172A; margin-bottom: 6px; letter-spacing: -0.8px; }
.sub-title { font-size: 15px; color: #475569; margin-bottom: 20px; }
.metric-card { height: 116px; background: #FFFFFF; border: 1px solid #E4EAF3; border-radius: 16px; padding: 19px 21px; display: flex; align-items: center; gap: 18px; }
.metric-icon { width: 58px; height: 58px; border-radius: 50%; display: flex; justify-content: center; align-items: center; font-size: 27px; font-weight: 900; }
.icon-blue { background: #EAF2FF; color: #0B63FF; } .icon-green { background: #DCFCE7; color: #16A34A; } .icon-red { background: #FEE2E2; color: #EF4444; } .icon-purple { background: #F3E8FF; color: #7E22CE; }
.metric-label { font-size: 14px; font-weight: 800; color: #334155; margin-bottom: 4px; }
.metric-value { font-size: 28px; font-weight: 950; color: #0F172A; line-height: 1.1; }
.metric-sub { font-size: 14px; color: #64748B; margin-top: 7px; }
.upload-box { border: 1.5px dashed #9FC2FF; border-radius: 15px; background: #FBFDFF; padding: 18px 20px; display: flex; align-items: center; gap: 16px; margin-bottom: 10px; }
.upload-icon { font-size: 36px; color: #0B63FF; } .upload-title { font-size: 18px; font-weight: 950; color: #0F172A; }
.viewer-card { background: #0B0F16; border-radius: 13px; overflow: hidden; border: 1px solid #1F2937; height: 420px; position: relative; }
.viewer-img { width: 100%; height: 420px; object-fit: cover; display: block; opacity: 0.96; }
.viewer-placeholder { height: 420px; background: linear-gradient(135deg, #111827, #020617); display: flex; justify-content: center; align-items: center; color: #94A3B8; font-size: 18px; font-weight: 800; }
.zoom-box { position: absolute; top: 16px; left: 16px; background: rgba(15, 23, 42, 0.82); color: #FFFFFF; border: 1px solid rgba(255,255,255,0.12); border-radius: 8px; padding: 9px 14px; font-size: 14px; font-weight: 800; display: flex; gap: 13px; align-items: center; z-index: 3; }
div[data-testid="stTabs"] { background: #FFFFFF; border: 1px solid #E4EAF3; border-radius: 16px; padding: 20px 18px; min-height: 420px; }
.result-box { border: 1px solid #E4EAF3; border-radius: 10px; padding: 14px; margin-bottom: 10px; background: #FFFFFF; }
.section-card { background: #FFFFFF; border: 1px solid #E4EAF3; border-radius: 16px; padding: 18px; }
.section-title { font-size: 17px; font-weight: 950; color: #0F172A; margin-bottom: 14px; }
</style>
""")


# ==================================================
# 👥 2. 왼쪽 고정 사이드바 조립 영역 (st.sidebar 이용)
# ==================================================
with st.sidebar:
    # [로고 영역]
    html("""
    <div class="sidebar-logo-area">
        <div class="sidebar-title"><span class="sidebar-logo-icon"></span> CellGuard AI</div>
        <div class="sidebar-subtitle">Battery Inspection</div>
    </div>
    """)
    
    # [네비게이션 메뉴]
    st.page_link("pages/exterior_inspection.py", label="🔍 Exterior Inspection", use_container_width=True)
    st.page_link("pages/ct_inspection.py", label="☢ CT Inspection", use_container_width=True)
    st.page_link("pages/inspection_report.py", label="📋 Inspection Report", use_container_width=True)
    
    # [작업자 정보 카드]
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M")
    current_operator = st.session_state.get("user_id", "1")
    html(f"""
    <div class="operator-card">
        <div class="operator-title">👤 Operator</div>
        <div class="operator-name">{current_operator}</div>
        <div class="operator-time">Access Time: {now_str}</div>
    </div>
    """)
    
    # [로그아웃 버튼]
    st.markdown('<div class="logout-btn-wrap">', unsafe_allow_html=True)
    if st.button("Logout", key="btn_logout"):
        st.session_state.login = False
        st.switch_page("streamlit_app.py")
    st.markdown('</div>', unsafe_allow_html=True)


# ==================================================
# 💻 3. 메인 대시보드 화면 영역 (쳐짐 문제 원천 차단)
# ==================================================
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
    return f"data:{uploaded_file.type or 'image/png'};base64,{base64.b64encode(uploaded_file.getvalue()).decode('utf-8')}"

# 메인 타이틀 구성
top_left, top_right = st.columns([2.35, 1.65])
with top_left:
    html('<div class="main-title">AI 배터리 외관 검사</div>')
    html('<div class="sub-title">배터리 외관 이미지를 업로드하여 정밀 분석을 수행합니다.</div>')

with top_right:
    f1, f2, f3 = st.columns([1, 1, 1.45])
    with f1: st.date_input("날짜", value=datetime.today(), label_visibility="collapsed")
    with f2: selected_line = st.selectbox("라인", ["전체 라인", "A Line", "B Line", "C Line"], label_visibility="collapsed")
    with f3: search_id = st.text_input("검색", placeholder="배터리 ID 검색", label_visibility="collapsed")

# 통계 카드 렌더링
m1, m2, m3, m4 = st.columns(4)
with m1: metric_card("전체 검사", "1,248 건", '↑ 12.5%', "▣", "icon-blue")
with m2: metric_card("정상", "982 건", "78.8%", "✓", "icon-green")
with m3: metric_card("불량", "266 건", "21.2%", "△", "icon-red")
with m4: metric_card("평균 시간", "1.8 초", '↓ 0.2초', "◷", "icon-purple")

html("<div style='height:15px;'></div>")

# 메인 작업 공간 및 업로더 구성
col_main, col_res = st.columns([2.35, 1])
with col_main:
    html('<div class="upload-box"><div class="upload-icon">☁</div><div class="upload-title">이미지 업로드</div></div>')
    u_col, a_col = st.columns([4, 1])
    with u_col: uploaded_file = st.file_uploader("파일", type=["jpg", "png"], label_visibility="collapsed")
    with a_col:
        if st.button("✣ AI 분석 시작", type="primary"):
            if uploaded_file:
                st.session_state.analysis_done = True
                
                # 분석 이력 자동 기록부 데이터 생성
                now = datetime.now()
                battery_id = f"B-{len(st.session_state.inspection_history) + 1:03d}"
                operator_id = str(st.session_state.get("user_id", "1"))
                
                # 1. 화면 출력용 세션 데이터 추가
                record = {
                    "배터리 ID": battery_id, "파일명": uploaded_file.name, "판정 결과": "불량",
                    "위험도": 82, "신뢰도": "92%", "검사 완료 시간": now.strftime("%Y-%m-%d %H:%M:%S"),
                    "작업자": operator_id, "라인": selected_line
                }
                st.session_state.inspection_history.insert(0, record)
                
                # 2. 💡 utils를 통해 data/reports.csv 파일에 누적 저장 연동 완료!
                save_inspection_report(
                    battery_id=battery_id, 
                    inspection_type="외관 검사", 
                    result="불량", 
                    risk_score=82, 
                    operator=operator_id, 
                    line=selected_line, 
                    confidence=0.92,  # 비율 형태로 통일 (0.92)
                    defect_summary="표면 크랙 발생", 
                    recommendation="정밀 재검사 필요", 
                    model_version="v1.0.0"
                )
                st.success(f"배터리 {battery_id} 분석 완료 및 CSV 기록 성공!")
            else:
                st.error("분석할 이미지를 업로드해 주세요.")

    # 뷰어 영역 출력
    image_src = uploaded_file_to_base64(uploaded_file)
    if image_src:
        html(f'<div class="viewer-card"><img class="viewer-img" src="{image_src}" /><div class="zoom-box"><span>100%</span></div></div>')
    else:
        html('<div class="viewer-card"><div class="viewer-placeholder">Battery Preview</div></div>')

with col_res:
    tabs = st.tabs(["분석 결과", "이미지 정보"])
    with tabs[0]:
        if st.session_state.analysis_done:
            html("""
            <div class="result-box">
                <div style="display:flex; justify-content:space-between; align-items:center;">
                    <span style="font-weight:800; color:#64748B;">판정 결과</span>
                    <span style="color:#EF1C1C; font-size:28px; font-weight:950;">불량</span>
                </div>
            </div>
            """)
        else:
            html('<div class="result-box" style="height:310px; display:flex; align-items:center; justify-content:center; text-align:center; color:#64748B;">분석 전입니다.</div>')

# 실시간 분석 데이터 차트 출력
with st.expander("📊 실시간 분석 통계", expanded=True):
    c1, c2 = st.columns(2)
    with c1: st.line_chart(pd.DataFrame({'검사수': [100, 150, 120, 200, 180]}, index=['10시', '11시', '12시', '13시', '14시']))
    with c2: st.bar_chart(pd.DataFrame({'불량': [10, 25, 15, 30, 20]}, index=['A', 'B', 'C', 'D', 'E']))

# 테이블 이력 출력
html("<div style='height:20px;'></div>")
df_hist = pd.DataFrame(st.session_state.inspection_history)
html('<div class="section-card"><div class="section-title">최근 검사 이력</div></div>')
if df_hist.empty:
    st.info("검사 데이터가 존재하지 않습니다.")
else:
    st.dataframe(df_hist, use_container_width=True, hide_index=True)