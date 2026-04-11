"""共享样式 & 工具函数"""

BRAND = "#7c3aed"
BRAND_LIGHT = "#a78bfa"
BRAND_SOFT = "rgba(124,58,237,0.08)"
GREEN = "#10b981"
RED = "#ef4444"
YELLOW = "#f59e0b"
BLUE = "#3b82f6"
GRAY = "#6b7280"
BG = "#ffffff"
BG_SOFT = "#f9fafb"

CSS = f"""
<style>
/* ── Reset & base ── */
[data-testid="stAppViewContainer"] {{
    background: {BG};
}}
[data-testid="stSidebar"] {{
    background: #1a0533 !important;
    border-right: 1px solid rgba(124,58,237,0.2);
}}
[data-testid="stSidebar"] * {{
    color: #e9d5ff !important;
}}
[data-testid="stSidebar"] .stSelectbox label,
[data-testid="stSidebar"] .stRadio label {{
    color: #c4b5fd !important;
    font-size: 12px;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.05em;
}}
[data-testid="stSidebar"] [data-testid="stSelectbox"] > div > div {{
    background: rgba(255,255,255,0.08) !important;
    border: 1px solid rgba(167,139,250,0.3) !important;
    color: white !important;
}}
/* ── Hide default header ── */
#MainMenu, footer, header {{ visibility: hidden; }}
/* ── Section titles ── */
.section-label {{
    font-size: 11px;
    font-weight: 700;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    color: {GRAY};
    margin-bottom: 6px;
}}
/* ── KPI Cards ── */
.kpi-card {{
    background: white;
    border: 1px solid #e5e7eb;
    border-radius: 16px;
    padding: 20px;
    box-shadow: 0 1px 6px rgba(0,0,0,0.05);
    text-align: center;
    transition: box-shadow 0.2s;
}}
.kpi-card:hover {{ box-shadow: 0 4px 20px rgba(124,58,237,0.12); }}
.kpi-value {{ font-size: 32px; font-weight: 900; line-height: 1; }}
.kpi-label {{ font-size: 11px; color: {GRAY}; font-weight: 600; text-transform: uppercase; letter-spacing: 0.08em; margin-top: 6px; }}
.kpi-delta {{ font-size: 12px; font-weight: 700; margin-top: 4px; }}
.kpi-delta-up {{ color: {GREEN}; }}
.kpi-delta-down {{ color: {RED}; }}
/* ── Status bar ── */
.status-bar {{
    background: linear-gradient(135deg, #1a0533 0%, #2d1b69 100%);
    border-radius: 14px;
    padding: 14px 24px;
    display: flex;
    align-items: center;
    gap: 24px;
    margin-bottom: 24px;
    flex-wrap: wrap;
}}
.status-item {{ display: flex; flex-direction: column; gap: 2px; }}
.status-label {{ font-size: 10px; color: #c4b5fd; font-weight: 600; letter-spacing: 0.1em; text-transform: uppercase; }}
.status-value {{ font-size: 14px; color: white; font-weight: 700; }}
.status-pill-ok {{
    background: rgba(16,185,129,0.18);
    color: #34d399;
    border-radius: 99px;
    padding: 4px 12px;
    font-size: 12px;
    font-weight: 700;
}}
/* ── Conclusion box ── */
.conclusion-box {{
    background: {BRAND_SOFT};
    border: 1px solid rgba(124,58,237,0.18);
    border-radius: 14px;
    padding: 16px 20px;
    margin: 16px 0;
}}
.conclusion-text {{ font-size: 15px; font-weight: 600; color: #1a0533; line-height: 1.5; }}
/* ── Action row ── */
.action-row {{
    display: flex;
    align-items: center;
    gap: 12px;
    padding: 14px 16px;
    border-radius: 12px;
    border: 1px solid #e5e7eb;
    background: white;
    margin-bottom: 8px;
    transition: border-color 0.15s;
}}
.action-row:hover {{ border-color: {BRAND_LIGHT}; }}
.priority-high {{ background: #fef2f2; color: {RED}; font-size: 10px; font-weight: 700; padding: 3px 10px; border-radius: 99px; }}
.priority-mid {{ background: #fffbeb; color: {YELLOW}; font-size: 10px; font-weight: 700; padding: 3px 10px; border-radius: 99px; }}
.priority-low {{ background: #f0fdf4; color: {GREEN}; font-size: 10px; font-weight: 700; padding: 3px 10px; border-radius: 99px; }}
/* ── Question rows ── */
.q-covered {{
    background: rgba(16,185,129,0.05);
    border: 1px solid rgba(16,185,129,0.2);
    border-radius: 10px;
    padding: 10px 14px;
    margin-bottom: 6px;
    font-size: 13px;
    color: #065f46;
}}
.q-missing {{
    background: rgba(239,68,68,0.05);
    border: 1px solid rgba(239,68,68,0.18);
    border-radius: 10px;
    padding: 10px 14px;
    margin-bottom: 6px;
    font-size: 13px;
    color: #991b1b;
}}
/* ── Delivery log ── */
.delivery-item {{
    display: flex;
    gap: 12px;
    padding: 12px 0;
    border-bottom: 1px solid #f3f4f6;
    align-items: flex-start;
}}
.delivery-dot {{
    width: 8px;
    height: 8px;
    border-radius: 50%;
    background: {BRAND};
    margin-top: 5px;
    flex-shrink: 0;
}}
/* ── Page header ── */
.page-header {{
    margin-bottom: 28px;
    padding-bottom: 16px;
    border-bottom: 1px solid #f3f4f6;
}}
.page-title {{ font-size: 26px; font-weight: 900; color: #0f0725; margin: 0; }}
.page-sub {{ font-size: 14px; color: {GRAY}; margin-top: 4px; }}
/* ── Warning strip ── */
.warn-strip {{
    background: linear-gradient(135deg, #7c2d12, #b45309);
    color: white;
    padding: 12px 20px;
    border-radius: 12px;
    font-size: 13px;
    font-weight: 600;
    margin: 12px 0;
}}
/* ── Score badge ── */
.score-a {{ color: {GREEN}; }}
.score-b {{ color: {YELLOW}; }}
.score-c {{ color: {RED}; }}
/* ── Remove streamlit padding ── */
.block-container {{ padding-top: 1.5rem !important; max-width: 1100px !important; }}
/* ── Sidebar logo area ── */
.sidebar-brand {{
    padding: 20px 0 16px;
    border-bottom: 1px solid rgba(124,58,237,0.25);
    margin-bottom: 20px;
    text-align: center;
}}
.sidebar-brand-name {{
    font-size: 20px;
    font-weight: 900;
    color: white;
    letter-spacing: -0.02em;
}}
.sidebar-brand-sub {{
    font-size: 11px;
    color: #a78bfa;
    margin-top: 2px;
}}
/* ── Nav active ── */
[data-testid="stSidebarNavLink"][aria-current="page"] {{
    background: rgba(124,58,237,0.2) !important;
    border-radius: 10px;
}}
</style>
"""

def inject_css():
    import streamlit as st
    st.markdown(CSS, unsafe_allow_html=True)

def status_bar(brand: str, platform: str, score: int, last_update: str):
    import streamlit as st
    grade = "A-" if score >= 80 else "B" if score >= 65 else "C"
    color = "#10b981" if score >= 80 else "#f59e0b" if score >= 65 else "#ef4444"
    st.markdown(f"""
    <div class="status-bar">
        <div class="status-item">
            <span class="status-label">当前品牌</span>
            <span class="status-value">🏷 {brand}</span>
        </div>
        <div class="status-item">
            <span class="status-label">监测平台</span>
            <span class="status-value">📡 {platform}</span>
        </div>
        <div class="status-item">
            <span class="status-label">AI可见度评分</span>
            <span class="status-value" style="color:{color}; font-size:18px;">{score} ({grade})</span>
        </div>
        <div class="status-item">
            <span class="status-label">最近更新</span>
            <span class="status-value">🕐 {last_update}</span>
        </div>
        <div style="margin-left:auto;">
            <span class="status-pill-ok">● 监测正常</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

def kpi_card(value: str, label: str, delta: str = "", delta_up: bool = True, color: str = "#7c3aed"):
    delta_class = "kpi-delta-up" if delta_up else "kpi-delta-down"
    delta_html = f'<div class="kpi-delta {delta_class}">{delta}</div>' if delta else ""
    return f"""
    <div class="kpi-card">
        <div class="kpi-value" style="color:{color}">{value}</div>
        <div class="kpi-label">{label}</div>
        {delta_html}
    </div>
    """

def conclusion_box(text: str):
    import streamlit as st
    st.markdown(f"""
    <div class="conclusion-box">
        <span style="font-size:16px;margin-right:8px;">💬</span>
        <span class="conclusion-text">{text}</span>
    </div>
    """, unsafe_allow_html=True)

def section_header(title: str, subtitle: str = ""):
    import streamlit as st
    sub = f'<p style="font-size:13px;color:#6b7280;margin:2px 0 0">{subtitle}</p>' if subtitle else ""
    st.markdown(f"""
    <div style="margin: 28px 0 14px">
        <p class="section-label">{title}</p>
        {sub}
    </div>
    """, unsafe_allow_html=True)

def sidebar_brand():
    import streamlit as st
    st.markdown("""
    <div class="sidebar-brand">
        <div class="sidebar-brand-name">智改<span style="color:#a78bfa">GEO</span></div>
        <div class="sidebar-brand-sub">AI 可见度管理后台</div>
    </div>
    """, unsafe_allow_html=True)
