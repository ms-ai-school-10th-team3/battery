import streamlit as st

def apply_global_style():
    st.markdown("""
    <style>
    /* 1. 사이드바 열기/닫기 버튼 위치 및 투명도 강제 조정 */
    /* 버튼이 있는 헤더 영역이 클릭을 방해하지 않도록 함 */
    header[data-testid="stHeader"] {
        background-color: rgba(0,0,0,0) !important;
        pointer-events: none !important;
        z-index: 999 !important;
    }

    /* 버튼 자체는 다시 클릭이 가능하게 설정 */
    header[data-testid="stHeader"] button {
        pointer-events: auto !important;
        visibility: visible !important;
        opacity: 0.8;
    }
    
    header[data-testid="stHeader"] button:hover {
        opacity: 1;
        background-color: rgba(0,0,0,0.05) !important;
    }

    /* 2. 푸터 및 불필요한 메뉴 숨기기 */
    footer, #MainMenu {
        visibility: hidden !important;
    }

    /* 3. 사이드바가 닫혔을 때 다시 여는 화살표(>) 버튼이 잘 보이도록 설정 */
    div[data-testid="collapsedControl"] {
        display: block !important;
        z-index: 1000 !important;
    }

    /* 4. 앱 배경색 및 컨테이너 패딩 */
    .stApp {
        background: #F8FBFF;
    }
    
    .block-container {
        padding-top: 4rem !important; /* 헤더 버튼과 겹치지 않게 본문을 내림 */
    }

    /* 사이드바 스타일 */
    section[data-testid="stSidebar"] {
        background: #FFFFFF !important;
        border-right: 1px solid #E5EAF3 !important;
    }
    </style>
    """, unsafe_allow_html=True)