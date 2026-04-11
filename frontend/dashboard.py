"""智改GEO 客户后台 V2 — 总览页"""
import sys, os
sys.path.insert(0, os.path.dirname(__file__))

import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
from datetime import datetime

from styles import inject_css, status_bar, kpi_card, conclusion_box, section_header, sidebar_brand, BRAND, GREEN, RED, YELLOW, BLUE, GRAY
from data import (
    get_brand_metrics, get_trend_data, get_questions,
    get_suggestions, get_deliveries, get_weekly_changes,
    get_last_update_time, BRANDS, PLATFORMS
)

st.set_page_config(
    page_title="智改GEO 后台",
    layout="wide",
    page_icon="🧠",
    initial_sidebar_state="expanded",
)
inject_css()

# ══════════════════════════════════════════
#  侧边栏
# ══════════════════════════════════════════
with st.sidebar:
    sidebar_brand()

    st.markdown('<p style="font-size:11px;font-weight:700;letter-spacing:0.1em;text-transform:uppercase;color:#c4b5fd;margin-bottom:6px">品牌</p>', unsafe_allow_html=True)
    brand = st.selectbox("品牌", list(BRANDS.keys()), label_visibility="collapsed", key="brand")

    st.markdown('<p style="font-size:11px;font-weight:700;letter-spacing:0.1em;text-transform:uppercase;color:#c4b5fd;margin:14px 0 6px">监测平台</p>', unsafe_allow_html=True)
    platform = st.selectbox("平台", PLATFORMS, label_visibility="collapsed", key="platform")

    st.markdown('<p style="font-size:11px;font-weight:700;letter-spacing:0.1em;text-transform:uppercase;color:#c4b5fd;margin:14px 0 6px">时间范围</p>', unsafe_allow_html=True)
    time_range = st.radio("时间", ["最近 7 天", "最近 30 天"], label_visibility="collapsed", key="time_range")

    st.markdown("<hr style='border-color:rgba(124,58,237,0.2);margin:20px 0'>", unsafe_allow_html=True)

    if st.button("🔄  刷新数据", use_container_width=True):
        st.rerun()

    st.markdown("<hr style='border-color:rgba(124,58,237,0.2);margin:16px 0'>", unsafe_allow_html=True)
    st.markdown("""
    <div style="font-size:11px;color:#7c3aed;font-weight:600;margin-bottom:8px">页面导航</div>
    """, unsafe_allow_html=True)
    pages = {
        "📊  总览": None,
        "📡  平台监控": "pages/2_平台监控",
        "🔍  类目/问题监控": "pages/3_类目问题监控",
        "⚡  优化建议": "pages/4_优化建议",
        "📄  报告中心": "pages/5_报告中心",
    }
    for name in pages:
        is_active = name.startswith("📊")
        bg = "rgba(124,58,237,0.2)" if is_active else "transparent"
        fw = "700" if is_active else "500"
        st.markdown(f"""
        <div style="padding:8px 12px;border-radius:8px;background:{bg};color:#e9d5ff;font-size:13px;font-weight:{fw};margin-bottom:2px">
            {name}
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<hr style='border-color:rgba(124,58,237,0.2);margin:16px 0'>", unsafe_allow_html=True)
    st.markdown('<div style="font-size:11px;color:#6b21a8;text-align:center">智改赋能深圳科技有限公司<br>© 2026</div>', unsafe_allow_html=True)

# ══════════════════════════════════════════
#  加载数据
# ══════════════════════════════════════════
days = 7 if time_range == "最近 7 天" else 30
m = get_brand_metrics(brand, platform)
trend_df = get_trend_data(brand, days)
questions = get_questions(brand)
suggestions = get_suggestions(brand)
deliveries = get_deliveries(brand)
changes = get_weekly_changes(brand)
last_update = get_last_update_time()

# ══════════════════════════════════════════
#  页头
# ══════════════════════════════════════════
st.markdown("""
<div class="page-header">
    <p class="page-title">📊 &nbsp;总览</p>
    <p class="page-sub">品牌 AI 可见度全局概览 — 先结论，后数据</p>
</div>
""", unsafe_allow_html=True)

# ── 状态条 ──
status_bar(brand, platform, m["score"], last_update)

# ── 一句话结论 ──
score = m["score"]
uncovered = m["uncovered_count"]
rec_rate = m["recommend_rate"]

if score >= 80 and uncovered <= 1:
    conclusion = f"本周 {brand} 表现良好，AI推荐覆盖率达 {rec_rate:.0f}%，整体可见度评分 {score}（{m['grade']}）。仍有 {uncovered} 个高价值场景待覆盖，建议本周优先处理。"
elif score >= 65:
    conclusion = f"{brand} 正在进入 AI 推荐路径，当前评分 {score}，推荐覆盖率 {rec_rate:.0f}%。有 {uncovered} 个高频场景未被覆盖，这是当前最大流量缺口。"
else:
    conclusion = f"{brand} 当前 AI 可见度较低（{score}分），仅 {rec_rate:.0f}% 的问题场景被推荐。{uncovered} 个高价值场景完全未覆盖，需要立即启动内容结构改造。"

conclusion_box(conclusion)

# ══════════════════════════════════════════
#  四大核心指标
# ══════════════════════════════════════════
section_header("核心指标", "点击各指标可查看详情")

col1, col2, col3, col4 = st.columns(4)
score_color = GREEN if score >= 80 else YELLOW if score >= 65 else RED
with col1:
    st.markdown(kpi_card(f"{score}", "AI 可见度评分", f"↑ +{m['delta_score']:.1f}", True, score_color), unsafe_allow_html=True)
with col2:
    st.markdown(kpi_card(f"{m['mentioned_rate']:.0f}%", "被推荐率", f"↑ +{m['delta_mentioned']:.1f}%", True, BLUE), unsafe_allow_html=True)
with col3:
    st.markdown(kpi_card(f"{m['total_prompts'] - uncovered}/{m['total_prompts']}", "覆盖问题数", f"共测试 {m['total_prompts']} 条", True, GREEN), unsafe_allow_html=True)
with col4:
    uncov_color = RED if uncovered >= 3 else YELLOW if uncovered >= 1 else GREEN
    st.markdown(kpi_card(f"{uncovered}", "未覆盖场景", "⚠️ 需关注" if uncovered > 0 else "✅ 全覆盖", uncovered == 0, uncov_color), unsafe_allow_html=True)

# ══════════════════════════════════════════
#  趋势图
# ══════════════════════════════════════════
section_header("趋势变化", f"过去 {days} 天 AI 可见度与引用率走势")

fig = go.Figure()
fig.add_trace(go.Scatter(
    x=trend_df["日期"], y=trend_df["AI可见度评分"],
    name="AI可见度评分", mode="lines+markers",
    line=dict(color=BRAND, width=2.5),
    marker=dict(size=5, color=BRAND),
    fill="tozeroy", fillcolor="rgba(124,58,237,0.06)",
))
fig.add_trace(go.Scatter(
    x=trend_df["日期"], y=trend_df["被引用率(%)"],
    name="被引用率(%)", mode="lines+markers",
    line=dict(color=BLUE, width=2, dash="dot"),
    marker=dict(size=4, color=BLUE),
))
fig.update_layout(
    height=260,
    margin=dict(l=0, r=0, t=10, b=0),
    paper_bgcolor="white",
    plot_bgcolor="white",
    font=dict(family="sans-serif", size=12, color="#374151"),
    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
    xaxis=dict(showgrid=False, tickformat="%m/%d", tickfont=dict(size=11)),
    yaxis=dict(showgrid=True, gridcolor="#f3f4f6", range=[0, 105], ticksuffix=""),
    hovermode="x unified",
)
fig.add_annotation(
    x=trend_df["日期"].iloc[-1], y=trend_df["AI可见度评分"].iloc[-1],
    text=f" {score}↑", showarrow=False,
    font=dict(size=12, color=BRAND, family="sans-serif"),
    xanchor="left",
)
st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

# ══════════════════════════════════════════
#  本周关键变化
# ══════════════════════════════════════════
section_header("本周关键变化", "影响 AI 可见度的重要变化")

for c in changes:
    if c["type"] == "up":
        icon, bg, border, tc = "↑", "#f0fdf4", "rgba(16,185,129,0.25)", "#065f46"
    else:
        icon, bg, border, tc = "⚠", "#fffbeb", "rgba(245,158,11,0.3)", "#78350f"
    st.markdown(f"""
    <div style="display:flex;align-items:center;gap:10px;padding:10px 14px;border-radius:10px;
        background:{bg};border:1px solid {border};margin-bottom:6px">
        <span style="font-size:14px;font-weight:900;color:{tc};width:16px;text-align:center">{icon}</span>
        <span style="font-size:13px;color:{tc};font-weight:500">{c['text']}</span>
    </div>
    """, unsafe_allow_html=True)

# ══════════════════════════════════════════
#  两列：未覆盖问题 + 优化建议
# ══════════════════════════════════════════
col_left, col_right = st.columns([1, 1], gap="large")

with col_left:
    section_header("未覆盖高价值问题", "这些场景是当前流量缺口")

    if questions["missing"]:
        for q in questions["missing"]:
            st.markdown(f"""
            <div class="q-missing">
                <span style="font-weight:700;margin-right:6px">✘</span>
                {q}<span style="float:right;font-size:11px;opacity:0.7">竞品可替代</span>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.markdown('<div style="color:#10b981;font-size:14px;font-weight:600">✅ 所有高价值问题均已覆盖</div>', unsafe_allow_html=True)

    if questions["covered"]:
        with st.expander(f"已覆盖问题（{len(questions['covered'])} 条）", expanded=False):
            for q in questions["covered"]:
                st.markdown(f'<div class="q-covered"><span style="font-weight:700;margin-right:6px">✔</span>{q}</div>', unsafe_allow_html=True)

with col_right:
    section_header("下一步优化建议", "按优先级排序，可直接执行")

    pri_style = {"高": "priority-high", "中": "priority-mid", "低": "priority-low"}
    for s in suggestions[:3]:
        st.markdown(f"""
        <div class="action-row">
            <span class="{pri_style.get(s['pri'], 'priority-low')}">{s['pri']}</span>
            <div style="flex:1">
                <div style="font-size:13px;font-weight:600;color:#111827">{s['title']}</div>
                <div style="font-size:11px;color:#6b7280;margin-top:2px">{s['impact']}</div>
            </div>
            <span style="font-size:11px;color:#a78bfa">→</span>
        </div>
        """, unsafe_allow_html=True)

    with st.expander("查看全部建议", expanded=False):
        for s in suggestions[3:]:
            st.markdown(f"""
            <div class="action-row">
                <span class="{pri_style.get(s['pri'], 'priority-low')}">{s['pri']}</span>
                <div style="flex:1">
                    <div style="font-size:13px;font-weight:600;color:#111827">{s['title']}</div>
                    <div style="font-size:11px;color:#6b7280;margin-top:2px">{s['impact']}</div>
                </div>
            </div>
            """, unsafe_allow_html=True)

# ══════════════════════════════════════════
#  最近交付动作
# ══════════════════════════════════════════
section_header("最近交付动作", "顾问团队已完成的工作")

type_colors = {"诊断": BRAND, "报告": BLUE, "方案": GREEN, "监测": YELLOW, "分析": "#f59e0b"}
for d in deliveries:
    tc = type_colors.get(d["type"], GRAY)
    st.markdown(f"""
    <div style="display:flex;gap:12px;padding:12px 0;border-bottom:1px solid #f3f4f6;align-items:center">
        <div style="width:8px;height:8px;border-radius:50%;background:{tc};flex-shrink:0;margin-top:2px"></div>
        <div style="flex:1;font-size:13px;color:#374151">{d['action']}</div>
        <div style="font-size:11px;color:#9ca3af;flex-shrink:0">{d['date']}</div>
        <div style="font-size:10px;font-weight:700;color:{tc};background:{tc}18;padding:2px 8px;border-radius:99px;flex-shrink:0">{d['type']}</div>
    </div>
    """, unsafe_allow_html=True)

# ══════════════════════════════════════════
#  底部 CTA
# ══════════════════════════════════════════
st.markdown("<div style='height:32px'></div>", unsafe_allow_html=True)

col_a, col_b, col_c = st.columns([1, 1, 2])
with col_a:
    if st.button("📄  导出本期报告", type="primary", use_container_width=True):
        st.success("✅ 报告生成中，请稍候…（功能开发中）")
with col_b:
    if st.button("💬  联系顾问", use_container_width=True):
        st.info("顾问微信：zggeo_service | 工作日 9:00–18:00")
with col_c:
    src_label = "（数据来源：真实监测）" if m.get("source") == "real" else "（数据为演示样例）"
    st.markdown(f'<p style="font-size:12px;color:#9ca3af;padding-top:8px">智改赋能深圳科技有限公司 · zggeo.com.cn &nbsp;{src_label}</p>', unsafe_allow_html=True)
