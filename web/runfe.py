# runfe.py
import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(
    page_title="CellGuard AI",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

st.markdown("""
<style>
    .stApp {
        background: #eef5ff;
    }

    .block-container {
        padding: 0 !important;
        max-width: 100% !important;
    }

    header, footer, #MainMenu {
        visibility: hidden;
    }

    div[data-testid="stToolbar"] {
        visibility: hidden;
    }
</style>
""", unsafe_allow_html=True)

html_code = """
<!DOCTYPE html>
<html lang="ko">
<head>
<meta charset="UTF-8" />
<style>
    * {
        font-family: 'Pretendard', 'Inter', 'Noto Sans KR', Arial, sans-serif;
        box-sizing: border-box;
    }

    body {
        margin: 0;
        background: #eef5ff;
    }

    .page {
        width: 100vw;
        min-height: 100vh;
        padding: 18px;
        background: #eef5ff;
    }

    .main-wrapper {
        width: 100%;
        height: calc(100vh - 36px);
        background: linear-gradient(135deg, #ffffff 0%, #f3f8ff 55%, #eaf3ff 100%);
        border: 1px solid #dbe8fb;
        border-radius: 22px;
        box-shadow: 0 14px 40px rgba(30, 83, 160, 0.10);
        overflow: hidden;
        display: grid;
        grid-template-columns: 39% 61%;
    }

    .left-panel {
        background: rgba(255,255,255,0.94);
        padding: 95px 88px 48px 88px;
        border-right: 1px solid #dbe8fb;
        display: flex;
        flex-direction: column;
    }

    .right-panel {
        position: relative;
        padding: 120px 68px 48px 68px;
        overflow: hidden;
        background:
            radial-gradient(circle at 78% 35%, rgba(58, 134, 255, 0.11), transparent 32%),
            radial-gradient(circle at 30% 48%, rgba(82, 147, 255, 0.09), transparent 26%),
            linear-gradient(135deg, #f8fbff 0%, #eef6ff 100%);
    }

    .logo-row {
        display: flex;
        align-items: center;
        gap: 14px;
        margin-left: 98px;
        margin-bottom: 55px;
    }

    .shield {
        width: 64px;
        height: 72px;
        background: linear-gradient(145deg, #0065ff, #0a4ee8);
        clip-path: polygon(50% 0%, 92% 15%, 92% 52%, 50% 100%, 8% 52%, 8% 15%);
        position: relative;
        box-shadow: 0 10px 20px rgba(0, 91, 255, 0.25);
    }

    .shield::after {
        content: "";
        position: absolute;
        width: 27px;
        height: 38px;
        top: 17px;
        left: 19px;
        background: rgba(255,255,255,0.88);
        clip-path: polygon(50% 0%, 82% 12%, 82% 54%, 50% 90%, 18% 54%, 18% 12%);
    }

    .brand-title {
        font-size: 34px;
        font-weight: 800;
        line-height: 1;
        color: #0065ff;
        letter-spacing: -1.2px;
    }

    .brand-sub {
        margin-top: 8px;
        font-size: 16px;
        color: #51617c;
        font-weight: 500;
    }

    .login-title {
        font-size: 40px;
        font-weight: 850;
        color: #07143d;
        letter-spacing: -1.6px;
        margin-bottom: 22px;
    }

    .login-desc {
        font-size: 17px;
        color: #4b5b78;
        margin-bottom: 44px;
        letter-spacing: -0.3px;
    }

    .form-label {
        font-size: 16px;
        color: #09193f;
        font-weight: 750;
        margin-bottom: 10px;
    }

    .input-box {
        height: 66px;
        width: 100%;
        border: 1.5px solid #cddaf0;
        border-radius: 8px;
        background: #ffffff;
        display: flex;
        align-items: center;
        padding: 0 21px;
        color: #98a6bd;
        font-size: 17px;
        margin-bottom: 28px;
        box-shadow: inset 0 1px 0 rgba(255,255,255,0.9);
    }

    .input-box .icon {
        font-size: 22px;
        margin-right: 16px;
        color: #7c8ba7;
    }

    .input-box .eye {
        margin-left: auto;
        color: #71809c;
        font-size: 21px;
    }

    .login-options {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-top: -5px;
        margin-bottom: 34px;
    }

    .remember {
        display: flex;
        align-items: center;
        gap: 13px;
        color: #081840;
        font-size: 16px;
        font-weight: 650;
    }

    .checkbox {
        width: 22px;
        height: 22px;
        border: 1.5px solid #b7c4dc;
        border-radius: 4px;
        background: #fff;
    }

    .forgot {
        color: #0065ff;
        font-size: 16px;
        font-weight: 800;
    }

    .btn-primary {
        width: 100%;
        height: 66px;
        border-radius: 8px;
        background: linear-gradient(180deg, #0067ff 0%, #0055f0 100%);
        color: white;
        font-size: 21px;
        font-weight: 800;
        display: flex;
        align-items: center;
        justify-content: center;
        box-shadow: 0 12px 25px rgba(0, 91, 255, 0.23);
        margin-bottom: 20px;
    }

    .btn-outline {
        width: 100%;
        height: 66px;
        border-radius: 8px;
        background: #ffffff;
        color: #0065ff;
        border: 1.8px solid #0065ff;
        font-size: 21px;
        font-weight: 850;
        display: flex;
        align-items: center;
        justify-content: center;
        margin-bottom: 54px;
    }

    .security-note {
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 13px;
        color: #7b89a3;
        font-size: 15px;
        line-height: 1.55;
        margin-top: auto;
    }

    .security-icon {
        width: 31px;
        height: 35px;
        border: 1.6px solid #7b89a3;
        border-radius: 9px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 15px;
    }

    .hero-title {
        text-align: center;
        color: #07194b;
        font-size: 32px;
        font-weight: 850;
        letter-spacing: -1.2px;
        margin-bottom: 16px;
        position: relative;
        z-index: 2;
    }

    .hero-subtitle {
        text-align: center;
        color: #43516b;
        font-size: 17px;
        margin-bottom: 65px;
        position: relative;
        z-index: 2;
    }

    .analysis-area {
        display: grid;
        grid-template-columns: 190px 1fr 195px;
        align-items: center;
        gap: 34px;
        margin-bottom: 66px;
        position: relative;
        z-index: 2;
    }

    .summary-card {
        height: 296px;
        background: rgba(255,255,255,0.94);
        border-radius: 16px;
        box-shadow: 0 15px 36px rgba(29, 82, 154, 0.11);
        padding: 25px 24px;
    }

    .card-title {
        font-size: 15px;
        color: #0c183c;
        font-weight: 850;
        margin-bottom: 20px;
    }

    .summary-item {
        display: flex;
        align-items: center;
        gap: 13px;
        margin-bottom: 18px;
    }

    .round-icon {
        width: 35px;
        height: 35px;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 17px;
        font-weight: 800;
    }

    .icon-blue {
        background: #e9f1ff;
        color: #0065ff;
    }

    .icon-green {
        background: #e8f8ef;
        color: #19b56d;
    }

    .icon-red {
        background: #ffe9ed;
        color: #ff334d;
    }

    .item-label {
        color: #4f5c77;
        font-size: 13px;
        font-weight: 650;
        margin-bottom: 3px;
    }

    .item-value {
        color: #0065ff;
        font-size: 20px;
        font-weight: 850;
        line-height: 1.1;
    }

    .item-value span {
        color: #4f5c77;
        font-size: 13px;
        font-weight: 650;
    }

    .battery-frame {
        height: 310px;
        position: relative;
        border-radius: 10px;
        background: rgba(255,255,255,0.38);
        display: flex;
        align-items: center;
        justify-content: center;
    }

    .corner {
        position: absolute;
        width: 35px;
        height: 35px;
        border-color: #0065ff;
        border-style: solid;
    }

    .corner.tl {
        top: -8px;
        left: -8px;
        border-width: 3px 0 0 3px;
        border-radius: 8px 0 0 0;
    }

    .corner.tr {
        top: -8px;
        right: -8px;
        border-width: 3px 3px 0 0;
        border-radius: 0 8px 0 0;
    }

    .corner.bl {
        bottom: -8px;
        left: -8px;
        border-width: 0 0 3px 3px;
        border-radius: 0 0 0 8px;
    }

    .corner.br {
        bottom: -8px;
        right: -8px;
        border-width: 0 3px 3px 0;
        border-radius: 0 0 8px 0;
    }

    .status-badge {
        position: absolute;
        right: 18px;
        top: 4px;
        background: linear-gradient(180deg, #006aff, #0057f0);
        color: #ffffff;
        font-size: 14px;
        font-weight: 850;
        padding: 8px 17px;
        border-radius: 8px;
        box-shadow: 0 10px 22px rgba(0, 91, 255, 0.24);
        z-index: 4;
    }

    .battery {
        position: relative;
        width: 395px;
        height: 132px;
        border-radius: 66px;
        background:
            linear-gradient(100deg, 
                #6f7b88 0%,
                #e9edf4 12%,
                #9da8b3 18%,
                #f7f9fc 33%,
                #c7d0db 47%,
                #f0f3f7 64%,
                #929da8 82%,
                #d9e0e8 100%);
        box-shadow:
            inset 18px 0 35px rgba(24,32,44,0.35),
            inset -18px 0 28px rgba(34,45,60,0.25),
            0 24px 38px rgba(55, 85, 130, 0.20);
        transform: rotate(-2deg);
        overflow: visible;
    }

    .battery::before {
        content: "";
        position: absolute;
        left: -28px;
        top: 25px;
        width: 70px;
        height: 82px;
        border-radius: 50%;
        background:
            radial-gradient(circle at center, #ebeff5 0 25%, #7a8490 27% 34%, #e8edf5 36% 52%, #616b78 55% 62%, #e2e8f0 64%);
        box-shadow: inset 10px 0 20px rgba(0,0,0,0.23);
    }

    .battery::after {
        content: "";
        position: absolute;
        right: -8px;
        top: 9px;
        width: 50px;
        height: 114px;
        border-radius: 50%;
        background: linear-gradient(90deg, #747f8a, #e9edf3 50%, #66717d);
        box-shadow: inset -8px 0 20px rgba(0,0,0,0.26);
    }

    .scratch {
        position: absolute;
        width: 96px;
        height: 24px;
        left: 215px;
        top: 69px;
        border-top: 5px solid #3a3b3e;
        border-radius: 50%;
        transform: rotate(8deg);
    }

    .scratch::after {
        content: "";
        position: absolute;
        left: 20px;
        top: 8px;
        width: 72px;
        height: 3px;
        background: #17191c;
        transform: rotate(-10deg);
        border-radius: 5px;
    }

    .detect-dot {
        position: absolute;
        width: 17px;
        height: 17px;
        border-radius: 50%;
        background: #ff3b4e;
        border: 3px solid rgba(255,255,255,0.85);
        box-shadow: 0 0 0 4px rgba(255,55,75,0.20);
        z-index: 5;
    }

    .dot1 { left: 205px; top: 35px; }
    .dot2 { left: 238px; top: 92px; }
    .dot3 { left: 273px; top: 70px; }

    .warning-triangle {
        position: absolute;
        right: 68px;
        top: 61px;
        width: 0;
        height: 0;
        border-left: 18px solid transparent;
        border-right: 18px solid transparent;
        border-bottom: 33px solid #ff4154;
        z-index: 5;
        filter: drop-shadow(0 3px 5px rgba(255,48,65,0.25));
    }

    .warning-triangle::after {
        content: "!";
        position: absolute;
        left: -4px;
        top: 11px;
        color: white;
        font-size: 19px;
        font-weight: 900;
    }

    .result-card {
        height: 286px;
        background: rgba(255,255,255,0.95);
        border-radius: 16px;
        box-shadow: 0 15px 36px rgba(29, 82, 154, 0.11);
        padding: 25px 24px;
    }

    .donut {
        width: 125px;
        height: 125px;
        margin: 25px auto 22px auto;
        border-radius: 50%;
        background: conic-gradient(#ff354d 0deg 76deg, #5a95ff 76deg 360deg);
        display: flex;
        align-items: center;
        justify-content: center;
        position: relative;
    }

    .donut::after {
        content: "";
        width: 78px;
        height: 78px;
        border-radius: 50%;
        background: white;
        position: absolute;
    }

    .donut-text {
        position: relative;
        z-index: 3;
        text-align: center;
        color: #07194b;
        font-weight: 900;
        font-size: 28px;
        line-height: 1;
    }

    .donut-text span {
        display: block;
        margin-top: 8px;
        color: #61708b;
        font-size: 12px;
        font-weight: 750;
    }

    .legend-row {
        display: grid;
        grid-template-columns: 16px 1fr auto;
        align-items: center;
        gap: 8px;
        margin-bottom: 12px;
        color: #51607c;
        font-size: 13px;
        font-weight: 750;
    }

    .legend-dot {
        width: 9px;
        height: 9px;
        border-radius: 50%;
    }

    .red { background: #ff354d; }
    .blue { background: #5a95ff; }
    .gray { background: #b9c2d0; }

    .feature-strip {
        height: 132px;
        border: 1px solid #cddcf1;
        border-radius: 12px;
        background: rgba(255,255,255,0.55);
        display: grid;
        grid-template-columns: 1fr 1fr 1fr;
        align-items: center;
        padding: 0 34px;
        position: relative;
        z-index: 2;
    }

    .feature-item {
        display: grid;
        grid-template-columns: 62px 1fr;
        gap: 18px;
        align-items: center;
        padding: 0 24px;
        min-height: 70px;
    }

    .feature-item:not(:last-child) {
        border-right: 1px solid #bccbe1;
    }

    .feature-icon {
        width: 58px;
        height: 58px;
        border-radius: 50%;
        background: #e8f1ff;
        display: flex;
        align-items: center;
        justify-content: center;
        color: #0065ff;
        font-size: 31px;
    }

    .feature-title {
        font-size: 16px;
        color: #07194b;
        font-weight: 850;
        margin-bottom: 8px;
    }

    .feature-desc {
        font-size: 13px;
        color: #5e6d86;
        line-height: 1.45;
        font-weight: 550;
    }

    .dot-pattern-left,
    .dot-pattern-right {
        position: absolute;
        width: 105px;
        height: 170px;
        background-image: radial-gradient(#a8c9ff 1.7px, transparent 1.7px);
        background-size: 18px 18px;
        opacity: 0.65;
        z-index: 0;
    }

    .dot-pattern-left {
        left: 62px;
        top: 145px;
    }

    .dot-pattern-right {
        right: 55px;
        top: 145px;
    }

    .wave {
        position: absolute;
        right: 55px;
        top: 180px;
        width: 420px;
        height: 160px;
        opacity: 0.35;
        background:
            repeating-radial-gradient(ellipse at center,
                transparent 0px,
                transparent 10px,
                rgba(100, 160, 255, 0.22) 11px,
                transparent 12px);
        border-radius: 50%;
        z-index: 0;
    }

    .copyright {
        position: absolute;
        right: 60px;
        bottom: 33px;
        color: #8a99b4;
        font-size: 13px;
        font-weight: 550;
    }

    @media (max-width: 1200px) {
        .main-wrapper {
            grid-template-columns: 1fr;
            height: auto;
        }

        .left-panel {
            padding: 60px;
        }

        .right-panel {
            padding: 70px 45px;
        }

        .analysis-area {
            grid-template-columns: 1fr;
        }
    }
</style>
</head>

<body>
<div class="page">
    <div class="main-wrapper">
        <section class="left-panel">
            <div class="logo-row">
                <div class="shield"></div>
                <div>
                    <div class="brand-title">CellGuard AI</div>
                    <div class="brand-sub">Battery Inspection Platform</div>
                </div>
            </div>

            <div class="login-title">품질 검사 시스템 로그인</div>
            <div class="login-desc">외관 검사, CT 내부검사, 검사 이력 및 보고서를 통합 관리합니다.</div>

            <div class="form-label">아이디</div>
            <div class="input-box">
                <span class="icon">♙</span>
                <span>아이디를 입력하세요</span>
            </div>

            <div class="form-label">비밀번호</div>
            <div class="input-box">
                <span class="icon">▣</span>
                <span>비밀번호를 입력하세요</span>
                <span class="eye">◎</span>
            </div>

            <div class="login-options">
                <div class="remember">
                    <div class="checkbox"></div>
                    <div>로그인 상태 유지</div>
                </div>
                <div class="forgot">비밀번호 찾기</div>
            </div>

            <div class="btn-primary">로그인</div>
            <div class="btn-outline">데모 체험</div>

            <div class="security-note">
                <div class="security-icon">⌂</div>
                <div>
                    보안이 중요한 시스템입니다.<br/>
                    안전한 계정만 접근할 수 있습니다.
                </div>
            </div>
        </section>

        <section class="right-panel">
            <div class="dot-pattern-left"></div>
            <div class="dot-pattern-right"></div>
            <div class="wave"></div>

            <div class="hero-title">AI 기반 배터리 품질 관리</div>
            <div class="hero-subtitle">정밀한 검사 · 신속한 분석 · 스마트한 의사결정</div>

            <div class="analysis-area">
                <div class="summary-card">
                    <div class="card-title">검사 요약</div>

                    <div class="summary-item">
                        <div class="round-icon icon-blue">▣</div>
                        <div>
                            <div class="item-label">검사 개수 수</div>
                            <div class="item-value">1,248 <span>건</span></div>
                        </div>
                    </div>

                    <div class="summary-item">
                        <div class="round-icon icon-green">✓</div>
                        <div>
                            <div class="item-label">정상</div>
                            <div class="item-value">982 <span>건 (78.8%)</span></div>
                        </div>
                    </div>

                    <div class="summary-item">
                        <div class="round-icon icon-red">△</div>
                        <div>
                            <div class="item-label">불량</div>
                            <div class="item-value">266 <span>건 (21.2%)</span></div>
                        </div>
                    </div>

                    <div class="summary-item">
                        <div class="round-icon icon-blue">⌁</div>
                        <div>
                            <div class="item-label">정상률</div>
                            <div class="item-value">78.8%</div>
                        </div>
                    </div>
                </div>

                <div class="battery-frame">
                    <div class="corner tl"></div>
                    <div class="corner tr"></div>
                    <div class="corner bl"></div>
                    <div class="corner br"></div>
                    <div class="status-badge">AI 분석 중</div>

                    <div class="battery">
                        <div class="scratch"></div>
                        <div class="detect-dot dot1"></div>
                        <div class="detect-dot dot2"></div>
                        <div class="detect-dot dot3"></div>
                        <div class="warning-triangle"></div>
                    </div>
                </div>

                <div class="result-card">
                    <div class="card-title">AI 분석 결과</div>

                    <div class="donut">
                        <div class="donut-text">
                            82%
                            <span>신뢰도</span>
                        </div>
                    </div>

                    <div class="legend-row">
                        <div class="legend-dot red"></div>
                        <div>불량</div>
                        <div>21.2%</div>
                    </div>

                    <div class="legend-row">
                        <div class="legend-dot blue"></div>
                        <div>정상</div>
                        <div>78.8%</div>
                    </div>

                    <div class="legend-row">
                        <div class="legend-dot gray"></div>
                        <div>기타</div>
                        <div>0.0%</div>
                    </div>
                </div>
            </div>

            <div class="feature-strip">
                <div class="feature-item">
                    <div class="feature-icon">▣</div>
                    <div>
                        <div class="feature-title">외관 검사</div>
                        <div class="feature-desc">AI 기반 이미지 분석으로<br/>미세 결함까지 정확하게 검출</div>
                    </div>
                </div>

                <div class="feature-item">
                    <div class="feature-icon">◇</div>
                    <div>
                        <div class="feature-title">CT 내부검사</div>
                        <div class="feature-desc">3D CT 스캔으로 내부 구조 및<br/>이상 징후를 정밀 분석</div>
                    </div>
                </div>

                <div class="feature-item">
                    <div class="feature-icon">▤</div>
                    <div>
                        <div class="feature-title">데이터 통합 관리</div>
                        <div class="feature-desc">검사 이력과 리포트를 통합 관리하여<br/>품질 추적 및 개선 지원</div>
                    </div>
                </div>
            </div>

            <div class="copyright">© 2026 CellGuard AI. All rights reserved.</div>
        </section>
    </div>
</div>
</body>
</html>
"""

components.html(html_code, height=950, scrolling=False)