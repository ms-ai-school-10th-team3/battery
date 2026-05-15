import streamlit as st
from utils.style import apply_global_style

st.set_page_config(
    page_title="CellGuard AI",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

apply_global_style()

# 로그인 상태 초기화
if "login" not in st.session_state:
    st.session_state["login"] = False

if "user_id" not in st.session_state:
    st.session_state["user_id"] = ""

# 이미 로그인되어 있으면 외관 검사 페이지로 이동
if st.session_state["login"]:
    st.switch_page("pages/exterior_inspection.py")


def login(user_id: str):
    st.session_state["login"] = True
    st.session_state["user_id"] = user_id
    st.switch_page("pages/exterior_inspection.py")


# 로그인 페이지 전용 스타일
st.markdown("""
<style>
    .block-container {
        padding-top: 2rem;
        padding-left: 2rem;
        padding-right: 2rem;
        max-width: 100%;
    }

    .stApp {
        background: #F3F8FF;
    }

    header, footer, #MainMenu {
        visibility: hidden;
    }

    div[data-testid="stTextInput"] input {
        height: 54px;
        border-radius: 10px;
        border: 1px solid #D7E0EF;
        font-size: 15px;
    }

    div[data-testid="stButton"] button {
        height: 54px;
        border-radius: 10px;
        font-size: 16px;
        font-weight: 800;
    }

    div[data-testid="stCheckbox"] label {
        color: #334155;
        font-weight: 600;
    }
</style>
""", unsafe_allow_html=True)


left, right = st.columns([0.39, 0.61], gap="large")

# =========================
# 왼쪽 로그인 영역
# =========================
with left:
    with st.container(border=True):
        st.write("")
        st.write("")
        st.markdown("## 🛡️ CellGuard AI")
        st.caption("Battery Inspection Platform")

        st.write("")
        st.write("")
        st.markdown("# 품질 검사 시스템 로그인")
        st.write("외관 검사, CT 내부검사, 검사 이력 및 보고서를 통합 관리합니다.")

        st.write("")
        st.write("")

        st.markdown("**아이디**")
        user_id = st.text_input(
            "아이디",
            placeholder="아이디를 입력하세요",
            label_visibility="collapsed",
            key="input_user_id"
        )

        st.markdown("**비밀번호**")
        password = st.text_input(
            "비밀번호",
            placeholder="비밀번호를 입력하세요",
            type="password",
            label_visibility="collapsed",
            key="input_password"
        )

        option_left, option_right = st.columns([1, 1])

        with option_left:
            st.checkbox("로그인 상태 유지")

        with option_right:
            st.markdown(
                "<p style='text-align:right; color:#0B63FF; font-weight:800;'>비밀번호 찾기</p>",
                unsafe_allow_html=True
            )

        if st.button("로그인", type="primary", use_container_width=True):
            if user_id.strip() == "" or password.strip() == "":
                st.error("아이디와 비밀번호를 입력해주세요.")
            else:
                login(user_id.strip())

        if st.button("데모 체험", use_container_width=True):
            login("demo_user")

        st.write("")
        st.write("")
        st.info("🛡️ 보안이 중요한 시스템입니다. 안전한 계정만 접근할 수 있습니다.")

# =========================
# 오른쪽 대시보드 미리보기 영역
# =========================
with right:
    with st.container(border=True):
        st.write("")
        st.write("")
        st.markdown(
            "<h1 style='text-align:center;'>AI 기반 배터리 품질 관리</h1>",
            unsafe_allow_html=True
        )
        st.markdown(
            "<p style='text-align:center; color:#475569;'>정밀한 검사 · 신속한 분석 · 스마트한 의사결정</p>",
            unsafe_allow_html=True
        )

        st.write("")
        st.write("")

        summary_col, image_col, result_col = st.columns([1, 2, 1], gap="large")

        with summary_col:
            with st.container(border=True):
                st.subheader("검사 요약")
                st.write("📋 검사 개수")
                st.markdown("### 1,248 건")
                st.write("✅ 정상")
                st.markdown("### 982 건")
                st.caption("78.8%")
                st.write("⚠️ 불량")
                st.markdown("### 266 건")
                st.caption("21.2%")
                st.write("📈 정상률")
                st.markdown("### 78.8%")

        with image_col:
            with st.container(border=True):
                st.markdown(
                    """
                    <div style="
                        height: 260px;
                        border: 3px solid #0B63FF;
                        border-radius: 18px;
                        display: flex;
                        justify-content: center;
                        align-items: center;
                        background: linear-gradient(90deg, #CBD5E1, #F8FAFC, #94A3B8);
                        color: #334155;
                        font-size: 22px;
                        font-weight: 900;
                    ">
                        Battery Image Preview
                    </div>
                    """,
                    unsafe_allow_html=True
                )
                st.success("AI 분석 중")

        with result_col:
            with st.container(border=True):
                st.subheader("AI 분석 결과")
                st.markdown(
                    "<h1 style='text-align:center;'>82%</h1>",
                    unsafe_allow_html=True
                )
                st.markdown(
                    "<p style='text-align:center; color:#64748B;'>신뢰도</p>",
                    unsafe_allow_html=True
                )
                st.write("🔴 불량 21.2%")
                st.write("🔵 정상 78.8%")
                st.write("⚪ 기타 0.0%")

        st.write("")
        st.write("")

        f1, f2, f3 = st.columns(3)

        with f1:
            with st.container(border=True):
                st.subheader("📷 외관 검사")
                st.write("AI 기반 이미지 분석으로 미세 결함까지 정확하게 검출합니다.")

        with f2:
            with st.container(border=True):
                st.subheader("🧊 CT 내부검사")
                st.write("내부 구조 및 이상 징후를 정밀 분석합니다.")

        with f3:
            with st.container(border=True):
                st.subheader("📄 데이터 통합 관리")
                st.write("검사 이력과 리포트를 통합 관리합니다.")

        st.write("")
        st.markdown(
            "<p style='text-align:right; color:#94A3B8;'>© 2026 CellGuard AI. All rights reserved.</p>",
            unsafe_allow_html=True
        )