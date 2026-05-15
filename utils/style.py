import streamlit as st

def apply_global_style():
    st.markdown("""
    <style>
    .stApp {
        background: #F8FBFF;
        color: #111827;
    }

    .block-container {
        padding-top: 2rem;
        padding-left: 2.5rem;
        padding-right: 2.5rem;
        max-width: 100%;
    }

    header, footer, #MainMenu {
        visibility: hidden;
    }

    section[data-testid="stSidebar"] {
        background: #FFFFFF;
        border-right: 1px solid #E5EAF3;
    }

    .main-title {
        font-size: 34px;
        font-weight: 900;
        color: #111827;
        margin-bottom: 6px;
    }

    .sub-title {
        font-size: 15px;
        color: #475569;
        margin-bottom: 24px;
    }

    .card {
        background: #FFFFFF;
        border: 1px solid #E5EAF3;
        border-radius: 18px;
        padding: 22px;
        box-shadow: 0 8px 24px rgba(15, 23, 42, 0.06);
    }

    .metric-card {
        background: #FFFFFF;
        border: 1px solid #E5EAF3;
        border-radius: 18px;
        padding: 22px;
        box-shadow: 0 8px 24px rgba(15, 23, 42, 0.06);
        min-height: 116px;
    }

    .metric-label {
        color: #475569;
        font-size: 14px;
        font-weight: 700;
    }

    .metric-value {
        color: #111827;
        font-size: 28px;
        font-weight: 900;
        margin-top: 8px;
    }

    .metric-sub {
        color: #2563EB;
        font-size: 13px;
        font-weight: 700;
        margin-top: 6px;
    }

    .upload-box {
        background: #F8FBFF;
        border: 1.8px dashed #9CC2FF;
        border-radius: 16px;
        padding: 20px;
        margin-bottom: 12px;
    }

    .image-viewer {
        background: #111827;
        border-radius: 16px;
        padding: 16px;
        min-height: 360px;
        display: flex;
        justify-content: center;
        align-items: center;
        color: white;
        font-size: 18px;
        font-weight: 700;
    }

    .result-title {
        color: #2563EB;
        font-size: 16px;
        font-weight: 900;
        border-bottom: 2px solid #2563EB;
        padding-bottom: 12px;
        margin-bottom: 16px;
    }

    .fail-text {
        color: #EF233C;
        font-size: 28px;
        font-weight: 900;
    }

    .normal-text {
        color: #16A34A;
        font-size: 28px;
        font-weight: 900;
    }

    .danger-score {
        font-size: 42px;
        font-weight: 900;
        color: #111827;
        text-align: center;
    }

    .tag-red {
        background: #FFE8E8;
        color: #EF233C;
        border-radius: 8px;
        padding: 5px 10px;
        font-size: 13px;
        font-weight: 800;
    }

    .tag-green {
        background: #E8F8EF;
        color: #16A34A;
        border-radius: 8px;
        padding: 5px 10px;
        font-size: 13px;
        font-weight: 800;
    }

    .tag-orange {
        background: #FFF3DC;
        color: #F97316;
        border-radius: 8px;
        padding: 5px 10px;
        font-size: 13px;
        font-weight: 800;
    }

    .sidebar-logo {
        font-size: 22px;
        font-weight: 900;
        color: #0B63FF;
        margin-bottom: 4px;
    }

    .sidebar-sub {
        font-size: 12px;
        color: #64748B;
        margin-bottom: 34px;
    }

    .operator-box {
        background: #F8FBFF;
        border: 1px solid #E5EAF3;
        border-radius: 16px;
        padding: 16px;
        margin-top: 24px;
    }

    div[data-testid="stButton"] button {
        border-radius: 10px;
        height: 44px;
        font-weight: 800;
    }

    div[data-testid="stTextInput"] input {
        border-radius: 10px;
        height: 44px;
    }

    div[data-testid="stSelectbox"] div {
        border-radius: 10px;
    }

    div[data-testid="stFileUploader"] {
        background: transparent;
    }
    </style>
    """, unsafe_allow_html=True)


def metric_card(label, value, sub="", icon=""):
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-label">{icon} {label}</div>
        <div class="metric-value">{value}</div>
        <div class="metric-sub">{sub}</div>
    </div>
    """, unsafe_allow_html=True)


def image_placeholder(title):
    st.markdown(f"""
    <div class="image-viewer">
        {title}
    </div>
    """, unsafe_allow_html=True)
    
def apply_custom_style():
    apply_global_style()