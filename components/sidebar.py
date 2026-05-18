import time

import streamlit as st


def render_sidebar(active_page: str):
    st.markdown(
        """
        <style>
        section[data-testid="stSidebar"] {
            display: block !important;
            visibility: visible !important;
            opacity: 1 !important;
            width: 250px !important;
            min-width: 250px !important;
            max-width: 250px !important;
            background: #FFFFFF !important;
            border-right: 1px solid #E5EAF3 !important;
            transform: translateX(0) !important;
        }

        section[data-testid="stSidebar"] > div {
            display: block !important;
            visibility: visible !important;
            width: 250px !important;
            min-width: 250px !important;
            max-width: 250px !important;
            padding: 22px 16px 16px 16px !important;
            background: #FFFFFF !important;
        }

        div[data-testid="stSidebarContent"] {
            display: block !important;
            visibility: visible !important;
            width: 250px !important;
            background: #FFFFFF !important;
        }

        .sidebar-logo {
            font-size: 22px;
            font-weight: 950;
            color: #0B63FF !important;
            margin-bottom: 2px;
            line-height: 1.2;
        }

        .sidebar-sub {
            font-size: 12px;
            font-weight: 700;
            color: #64748B !important;
            margin-bottom: 28px;
            padding-left: 34px;
        }

        .sidebar-section-gap {
            height: 54px;
        }

        section[data-testid="stSidebar"] * {
            color: #334155 !important;
        }

        section[data-testid="stSidebar"] a {
            display: flex !important;
            align-items: center !important;
            min-height: 40px !important;
            color: #334155 !important;
            text-decoration: none !important;
            font-weight: 850 !important;
            border-radius: 10px !important;
            padding: 8px 10px !important;
            margin-bottom: 8px !important;
        }

        section[data-testid="stSidebar"] a:hover {
            background: #EEF4FF !important;
            color: #0B63FF !important;
        }

        section[data-testid="stSidebar"] a:hover * {
            color: #0B63FF !important;
        }

        section[data-testid="stSidebar"] a[aria-current="page"] {
            background: #EEF4FF !important;
            color: #0B63FF !important;
            font-weight: 950 !important;
            border-left: 4px solid #0B63FF !important;
        }

        section[data-testid="stSidebar"] a[aria-current="page"] * {
            color: #0B63FF !important;
            font-weight: 950 !important;
        }

        .operator-box {
            background: #F8FBFF;
            border: 1px solid #E5EAF3;
            border-radius: 14px;
            padding: 14px;
            margin-top: 22px;
            margin-bottom: 14px;
            font-size: 13px;
            line-height: 1.7;
            color: #334155 !important;
        }

        .operator-title {
            font-size: 14px;
            font-weight: 900;
            color: #111827 !important;
        }

        .operator-id {
            font-size: 13px;
            font-weight: 800;
            color: #334155 !important;
        }

        .access-time {
            font-size: 11px;
            color: #64748B !important;
        }

        section[data-testid="stSidebar"] .stButton > button {
            width: 100%;
            height: 38px;
            border-radius: 10px;
            border: 1px solid #D7E1F2 !important;
            background: #FFFFFF !important;
            color: #111827 !important;
            font-weight: 800 !important;
            font-size: 13px !important;
        }

        section[data-testid="stSidebar"] .stButton > button:hover {
            border-color: #0B63FF !important;
            color: #0B63FF !important;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

    with st.sidebar:
        st.markdown(
            """
            <div class="sidebar-logo">🛡️ CellGuard AI</div>
            <div class="sidebar-sub">Battery Inspection</div>
            """,
            unsafe_allow_html=True,
        )

        st.page_link(
            "pages/exterior_inspection.py",
            label="Exterior Inspection",
            icon="🔍",
        )

        st.page_link(
            "pages/ct_inspection.py",
            label="CT Inspection",
            icon="☢️",
        )

        st.page_link(
            "pages/inspection_report.py",
            label="Inspection Report",
            icon="📋",
        )

        st.markdown('<div class="sidebar-section-gap"></div>', unsafe_allow_html=True)

        user_id = st.session_state.get("user_id", "Guest")

        st.markdown(
            f"""
            <div class="operator-box">
                <div class="operator-title">👤 Operator</div>
                <div class="operator-id">{user_id}</div>
                <br>
                <div class="access-time">
                    Access Time: {time.strftime("%Y-%m-%d %H:%M")}
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        if st.button("Logout", use_container_width=True):
            st.session_state["login"] = False
            st.session_state["user_id"] = ""
            st.switch_page("streamlit_app.py")
