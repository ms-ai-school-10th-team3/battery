import streamlit as st
import pandas as pd
import time

# 1. 페이지 설정 (화면을 넓게 사용)
st.set_page_config(layout="wide", page_title="CellGuard AI Dashboard")

# 2. 커스텀 스타일 적용
st.markdown("""
    <style>
    .stApp { background-color: #F8FAFC; }
    [data-testid="stMetric"] {
        background-color: white;
        padding: 15px;
        border-radius: 10px;
        border: 1px solid #E2E8F0;
        box-shadow: 0 2px 5px rgba(0,0,0,0.05);
    }
    </style>
""", unsafe_allow_html=True)

# 3. 사이드바 메뉴 (LNB)
with st.sidebar:
    st.title("🛡️ CellGuard AI")
    menu = st.radio("메뉴 선택", ["외관 검사", "CT 내부 검사", "검사 이력 / 보고서"])
    st.divider()
    st.write("👤 작업자: **y1nature**") # 깃허브 아이디로 수정해드렸어요!
    st.caption(f"접속 시간: {time.strftime('%Y-%m-%d %H:%M')}")

# 4. 메뉴 1: 외관 검사 화면
if menu == "외관 검사":
    st.title("🔍 AI 배터리 외관 검사")
    st.caption("배터리 외관 이미지를 분석하여 결함 및 위험도를 판정합니다.")
    
    # 상단 지표
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("오늘 전체 검사", "1,248 건", "↑ 12.5%")
    col2.metric("정상", "982 건", "78.8%")
    col3.metric("불량", "266 건", "21.2%")
    col4.metric("평균 시간", "1.8s", "↓ 0.2s")
    
    st.divider()
    
    left, right = st.columns([2, 1])
    with left:
        st.subheader("🖼️ 이미지 분석")
        uploaded_file = st.file_uploader("배터리 이미지를 업로드하세요", type=["jpg", "png"])
        if uploaded_file:
            st.image(uploaded_file, caption="분석 대상 이미지", use_container_width=True)
        else:
            st.info("이미지를 업로드하면 AI 분석이 시작됩니다.")
            st.image("https://raw.githubusercontent.com/ajndkr/lan-segmentation/master/images/battery_sample.jpg", caption="[샘플 데이터] 대기 중", use_container_width=True)
            
    with right:
        st.subheader("📊 판정 결과")
        if uploaded_file:
            st.error("판정: 불량 (FAIL)")
            st.warning("⚠️ Swelling(팽창) 의심")
            st.write("**위험도 점수**")
            st.progress(82)
            st.write("82% - 고위험군")
        else:
            st.write("이미지를 업로드하면 결과가 표시됩니다.")

# 5. 메뉴 2: CT 내부 검사 화면
elif menu == "CT 내부 검사":
    st.title("☢️ AI 배터리 CT 내부검사")
    st.caption("CT 단면 이미지를 기반으로 내부 결함을 정밀 분석합니다.")
    
    with st.container(border=True):
        up1, up2 = st.columns([4, 1])
        up1.file_uploader("CT 이미지 파일(DICOM) 선택", type=["dcm", "tiff"])
        up2.write(""); up2.button("🚀 AI 분석 실행", type="primary", use_container_width=True)

    v_col, i_col = st.columns([3, 1.2])
    with v_col:
        # CT 샘플 이미지
        st.image("https://img.medicalexpo.com/images_me/photo-g/70742-12623326.jpg", use_container_width=True)
        st.slider("슬라이스 이동", 0, 512, 114)
        
    with i_col:
        st.markdown("### 판정: <span style='color:red;'>불량</span>", unsafe_allow_html=True)
        st.error("❌ 전극 정렬 이상\n\n❌ 내부 공극(Gap) 발생")
        st.write("**위험도**")
        st.progress(76)
        st.write("🔥 **높음 (76%)**")

# 6. 메뉴 3: 검사 이력 / 보고서
else:
    st.title("📋 검사 이력 및 보고서")
    
    # 필터
    f1, f2, f3 = st.columns([2, 1, 1])
    f1.date_input("조회 기간")
    f2.selectbox("라인", ["전체", "A-Line", "B-Line"])
    f3.selectbox("유형", ["전체", "외관", "CT"])

    # 샘플 데이터 테이블
    hist_df = pd.DataFrame([
        {"ID": "B-001", "유형": "외관", "결과": "불량", "위험도": "82%", "시간": "2026-05-13 14:32"},
        {"ID": "B-002", "유형": "CT", "결과": "정상", "위험도": "12%", "시간": "2026-05-13 14:28"},
        {"ID": "B-003", "유형": "외관", "결과": "보통", "위험도": "45%", "시간": "2026-05-13 14:25"},
    ])

    st.divider()
    l_col, r_col = st.columns([3, 2])
    
    with l_col:
        st.subheader("검사 목록")
        st.dataframe(hist_df, use_container_width=True, hide_index=True)
        st.download_button("📥 CSV 내보내기", data=hist_df.to_csv().encode('utf-8-sig'), file_name="history.csv")

    with r_col:
        st.subheader("📄 상세 리포트")
        st.info("목록에서 행을 선택하면 상세 정보가 나타납니다.")
        # 선택 시연용 박스
        with st.container(border=True):
            st.write("### 배터리 ID: B-001")
            st.write("**결과:** 불량 | **위험도:** 82%")
            st.image("https://raw.githubusercontent.com/ajndkr/lan-segmentation/master/images/battery_sample.jpg", use_container_width=True)
            st.button("📥 PDF 다운로드", use_container_width=True)
