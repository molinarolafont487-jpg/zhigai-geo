"""智改GEO 客户后台 V2 — 总览页"""
import sys, os
sys.path.insert(0, os.path.dirname(__file__))

import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
from datetime import datetime
from pathlib import Path
import json
import os
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas

from styles import inject_css, status_bar, kpi_card, conclusion_box, section_header, sidebar_brand, BRAND, GREEN, RED, YELLOW, BLUE, GRAY
from data import (
    get_brand_metrics, get_trend_data, get_questions,
    get_suggestions, get_deliveries, get_weekly_changes,
    get_last_update_time, log_execution, BRANDS, PLATFORMS
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

if "trend_days" not in st.session_state:
    st.session_state.trend_days = 30
if "show_contact" not in st.session_state:
    st.session_state.show_contact = False
if "queue_count" not in st.session_state:
    st.session_state.queue_count = 0
if "report_ready" not in st.session_state:
    st.session_state.report_ready = False
if "report_path" not in st.session_state:
    st.session_state.report_path = ""
if "queue_items" not in st.session_state:
    st.session_state.queue_items = []

# ══════════════════════════════════════════
#  加载数据
# ══════════════════════════════════════════
days = 7 if time_range == "最近 7 天" else 30
m = get_brand_metrics(brand, platform)
days = st.session_state.trend_days
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
<div class="page-header" style="padding-top:0;margin-top:-6px;display:flex;align-items:center;gap:12px;">
    <div style="width:34px;height:34px;border-radius:10px;background:#111827;color:#ffffff;display:flex;align-items:center;justify-content:center;font-size:20px;font-weight:900;box-shadow:0 6px 14px rgba(17,24,39,0.18)">Z</div>
    <div>
        <p class="page-title" style="margin:0">总览</p>
        <p class="page-sub" style="margin:4px 0 0 0">品牌 AI 可见度全局概览 — 先结论，后数据</p>
    </div>
</div>
""", unsafe_allow_html=True)

score = m["score"]
uncovered = m["uncovered_count"]
rec_rate = m["recommend_rate"]
mentioned_rate = m["mentioned_rate"]
citation_rate = m.get("citation_rate", 58)
entry_rate = max(0, min(100, 100 - uncovered * 10))

if score >= 80 and rec_rate >= 80:
    status_text = "你的品牌当前状态：已进入基础推荐路径"
    status_bg = "linear-gradient(135deg,#064e3b,#065f46)"
    status_border = "rgba(16,185,129,0.35)"
elif score >= 60:
    status_text = "你的品牌当前状态：偶尔被提及，但还没进入稳定推荐区"
    status_bg = "linear-gradient(135deg,#78350f,#92400e)"
    status_border = "rgba(245,158,11,0.35)"
else:
    status_text = "你的品牌当前状态：可见度不足，尚未进入稳定推荐区"
    status_bg = "linear-gradient(135deg,#7f1d1d,#991b1b)"
    status_border = "rgba(239,68,68,0.35)"

cta_left, cta_right = st.columns([4, 1.2], gap="small")
with cta_left:
    st.markdown(f"""
    <div style="padding:16px 18px;border-radius:14px;background:{status_bg};border:1px solid {status_border};margin:16px 0 18px 0;">
      <div style="font-size:12px;color:#e5e7eb;opacity:0.9;margin-bottom:4px;">顶部状态结论</div>
      <div style="font-size:20px;font-weight:800;color:white;line-height:1.4;">{status_text}</div>
    </div>
    """, unsafe_allow_html=True)
with cta_right:
    if st.button("📄 导出本周报告", use_container_width=True, type="primary"):
        today = datetime.now().strftime('%Y%m%d')
        md_path = f"monitor_results/智改GEO_本周监测报告_{brand}_{today}.md"
        pdf_path = f"monitor_results/智改GEO_本周监测报告_{brand}_{today}.pdf"
        report_body = f"# 智改GEO 本周监测报告\n\n## 封面信息\n- 品牌：{brand}\n- 日期：{datetime.now().strftime('%Y-%m-%d %H:%M')}\n- 平台：{platform}\n\n## 核心指标摘要\n| 指标 | 数值 |\n|---|---:|\n| AI 可见度评分 | {score} |\n| 被提及率 | {mentioned_rate:.0f}% |\n| 被引用率 | {citation_rate:.0f}% |\n| 推荐路径进入率 | {entry_rate:.0f}% |\n\n## 流量流失问题\n"
        for item in questions.get('missing', [])[:5]:
            report_body += f"- {item['question']}｜{item['status']}｜{item['priority']}｜{item['action']}\n"
        report_body += "\n## 优化建议\n"
        for s in suggestions[:3]:
            report_body += f"- {s['title']}\n  - 为什么要做：{s.get('detail','')}\n  - 预期效果：{s.get('impact','')}\n"
        report_body += f"\n---\n智改赋能深圳科技有限公司 | {brand} 周报\n"
        with open(md_path, "w", encoding="utf-8") as f:
            f.write(report_body)
        try:
            c = canvas.Canvas(pdf_path, pagesize=A4)
            y = 800
            for line in report_body.splitlines():
                c.drawString(40, y, line[:90])
                y -= 18
                if y < 50:
                    c.showPage()
                    y = 800
            c.save()
            st.session_state.report_ready = True
            st.session_state.report_path = pdf_path
            st.success(f"PDF 报告已生成：{pdf_path}")
        except Exception as e:
            st.session_state.report_ready = True
            st.session_state.report_path = md_path
            st.error(f"PDF 生成失败，已回退为 Markdown 下载：{e}")
    if st.button("💬 联系顾问", use_container_width=True):
        st.session_state.show_contact = not st.session_state.show_contact

if st.session_state.report_ready and st.session_state.report_path:
    report_file = st.session_state.report_path
    if report_file.endswith('.pdf'):
        with open(report_file, 'rb') as f:
            st.download_button("⬇️ 下载本周报告", data=f.read(), file_name=report_file.split('/')[-1], mime="application/pdf")
    else:
        with open(report_file, "r", encoding="utf-8") as f:
            st.download_button("⬇️ 下载本周报告", data=f.read(), file_name=report_file.split('/')[-1], mime="text/markdown")

if st.session_state.show_contact:
    outer_left, outer_mid, outer_right = st.columns([1, 2.2, 1])
    with outer_mid:
        st.markdown("""
        <div style='background:#1f2937;border:1px solid rgba(255,255,255,0.08);border-radius:20px;padding:28px 30px 22px 30px;margin-top:14px;box-shadow:0 18px 36px rgba(0,0,0,0.32)'>
            <div style='font-size:30px;font-weight:900;color:#ffffff;margin-bottom:10px;text-align:center'>联系顾问</div>
            <div style='font-size:16px;color:#e2e8f0;margin-bottom:6px;text-align:center'>我们将在24小时内回复您</div>
            <div style='font-size:13px;color:#94a3b8;text-align:center;margin-bottom:18px'>提交问题后，我们会通过企业微信优先回复</div>
        </div>
        """, unsafe_allow_html=True)
        st.markdown("""
        <div style='background:#0f172a;border:1px solid rgba(255,255,255,0.08);border-radius:18px;padding:22px 22px 18px 22px;margin-top:6px'>
            <div style='color:#10b981;font-size:14px;font-weight:900;margin-bottom:12px;text-align:center'>联系方式</div>
            <div style='color:#f8fafc;font-size:15px;line-height:2;text-align:center'>
                企业微信：zggeo88<br>
                电话：0755-22288899<br>
                邮箱：zhigaigeo@zhigaifuneng.cn
            </div>
            <div style='color:#94a3b8;font-size:12px;text-align:center;margin-top:10px'>提交问题后，我们会通过企业微信优先回复</div>
        </div>
        """, unsafe_allow_html=True)
        st.markdown("""
        <div style='background:#0f172a;border:1px solid rgba(255,255,255,0.08);border-radius:18px;padding:18px 22px;margin-top:10px'>
            <div style='color:#10b981;font-size:14px;font-weight:900;margin-bottom:12px;text-align:center'>联系方式</div>
            <div style='color:#f8fafc;font-size:15px;line-height:2;text-align:center'>
                企业微信：zggeo88<br>
                电话：0755-22288899<br>
                邮箱：zhigaigeo@zhigaifuneng.cn
            </div>
        </div>
        """, unsafe_allow_html=True)
        st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)
        with st.form("contact_form"):
            c1, c2 = st.columns(2)
            with c1:
                category = st.selectbox("问题类型", ["内容优化", "推荐率提升", "负面风险修复", "其他"])
            with c2:
                urgency = st.selectbox("紧急程度", ["中", "高", "低"])
            question = st.text_area("请简要描述您的问题", placeholder="例如：我想优先提升 Claude Pro 相关问题的推荐率", height=110)
            submitted = st.form_submit_button("提交咨询请求", type="primary", use_container_width=True)
            if submitted:
                with open("monitor_results/contact_requests.log", "a", encoding="utf-8") as f:
                    f.write(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | {brand} | {category} | {urgency} | {question}\n")
                webhook_path = Path("monitor_results/wecom_webhook_placeholder.json")
                if not webhook_path.exists():
                    webhook_path.write_text(json.dumps({"wecom_webhook": "待配置"}, ensure_ascii=False, indent=2), encoding="utf-8")
                st.markdown("<div style='background:#065f46;border:1px solid rgba(16,185,129,0.45);color:#ecfdf5;padding:12px 14px;border-radius:12px;font-size:14px;font-weight:700;margin-top:10px;text-align:center'>已提交成功，我们将通过企业微信（zggeo88）在24小时内回复您。</div>", unsafe_allow_html=True)

if score >= 80 and uncovered <= 1:
    conclusion = f"你现在已经进入基础推荐路径，核心问题不是有没有曝光，而是如何把零散提及变成稳定推荐。本周推荐路径进入率 {entry_rate:.0f}%，仍有 {uncovered} 个高价值问题会让潜在客户流失。"
elif score >= 65:
    conclusion = f"你现在处在“偶尔被提及”的阶段，说明品牌已经被部分 AI 看到，但还没有形成稳定推荐。当前有 {uncovered} 个高价值问题未覆盖，这是最直接的流量流失点。"
else:
    conclusion = f"你现在最大的风险不是转化低，而是很多客户提问时根本看不到你。当前可见度评分只有 {score}，推荐路径进入率仅 {entry_rate:.0f}%，需要先补核心问题覆盖。"

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
    st.markdown(kpi_card(f"{mentioned_rate:.0f}%", "被提及率", f"↑ +{m['delta_mentioned']:.1f}%", True, BLUE), unsafe_allow_html=True)
with col3:
    st.markdown(kpi_card(f"{citation_rate:.0f}%", "被引用率", "内容证据被 AI 采用的比例", True, GREEN), unsafe_allow_html=True)
with col4:
    entry_color = GREEN if entry_rate >= 80 else YELLOW if entry_rate >= 60 else RED
    st.markdown(kpi_card(f"{entry_rate:.0f}%", "推荐路径进入率", f"未覆盖问题 {uncovered} 个", entry_rate >= 80, entry_color), unsafe_allow_html=True)

# ══════════════════════════════════════════
#  趋势图
# ══════════════════════════════════════════
section_header("趋势变化", f"过去 {days} 天 AI 可见度与引用率走势")
tr1, tr2, tr3 = st.columns([1,1,1])
with tr1:
    if st.button("7天", use_container_width=True, type="primary" if st.session_state.trend_days == 7 else "secondary"):
        st.session_state.trend_days = 7
        st.rerun()
with tr2:
    if st.button("30天", use_container_width=True, type="primary" if st.session_state.trend_days == 30 else "secondary"):
        st.session_state.trend_days = 30
        st.rerun()
with tr3:
    if st.button("90天", use_container_width=True, type="primary" if st.session_state.trend_days == 90 else "secondary"):
        st.session_state.trend_days = 90
        st.rerun()

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
    section_header("这些问题是当前流量流失的主要入口", "客户在这些问题上找不到你，就会直接流向竞品")

    if questions["missing"]:
        st.markdown("""
        <div style='display:grid;grid-template-columns:2.2fr 0.8fr 1fr 0.6fr 1.3fr;padding:10px 12px;background:#f8fafc;border:1px solid #e5e7eb;border-radius:10px;font-size:12px;font-weight:700;color:#334155;margin-bottom:8px'>
            <div>问题内容</div><div>所属平台</div><div>当前状态</div><div>优先级</div><div>建议行动</div>
        </div>
        """, unsafe_allow_html=True)
        sorted_missing = sorted(questions["missing"], key=lambda x: {"高":0,"中":1,"低":2}.get(x["priority"], 9))
        for item in sorted_missing:
            highlight = "#fef2f2" if item["priority"] == "高" else "#ffffff"
            border = "#fecaca" if item["priority"] == "高" else "#e5e7eb"
            st.markdown(f"""
            <div style='display:grid;grid-template-columns:2.2fr 0.8fr 1fr 0.6fr 1.3fr;padding:12px;background:{highlight};border:1px solid {border};border-radius:10px;font-size:12px;color:#374151;margin-bottom:8px;align-items:center'>
                <div style='font-weight:600'>{item['question']}</div>
                <div>{item['platform']}</div>
                <div>{item['status']}</div>
                <div style='font-weight:700;color:#7c3aed'>{item['priority']}</div>
                <div>{item['action']}</div>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.markdown('<div style="color:#10b981;font-size:14px;font-weight:600">✅ 当前高价值问题已基本覆盖，可开始做转化型优化</div>', unsafe_allow_html=True)

with col_right:
    section_header("下一步优化建议", "先做最影响成交的 3 件事")

    pri_style = {"高": "priority-high", "中": "priority-mid", "低": "priority-low"}
    for idx, s in enumerate(suggestions[:3]):
        why = s.get('detail', '这项动作会直接影响品牌被推荐与被信任的概率')
        effect = s.get('impact', '预计可见度可提升 10-20 分')
        st.markdown(f"""
        <div class="action-row" style="align-items:flex-start">
            <span class="{pri_style.get(s['pri'], 'priority-low')}">{s['pri']}</span>
            <div style="flex:1">
                <div style="font-size:13px;font-weight:700;color:#111827">{s['title']}</div>
                <div style="font-size:11px;color:#374151;margin-top:4px">为什么要做：{why}</div>
                <div style="font-size:11px;color:#059669;margin-top:4px">预期效果：{effect}</div>
                <div style="font-size:11px;color:#7c3aed;margin-top:4px">建议优先级：{s['pri']}</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        if st.button(f"立即执行_{idx+1}", key=f"exec_{idx}", use_container_width=True):
            log_execution(brand, s['title'])
            now_str = datetime.now().strftime('%Y-%m-%d %H:%M')
            st.session_state.queue_count += 1
            st.session_state.queue_items.append({"title": s['title'], "priority": s['pri'], "time": now_str, "status": "待处理"})
            st.success(f"已加入本周优化队列，当前队列共 {st.session_state.queue_count} 条任务")

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

    section_header("本周优化队列", f"当前共有 {st.session_state.queue_count} 条任务")
    if st.session_state.queue_items:
        st.markdown("""
        <div style='display:grid;grid-template-columns:2fr 0.8fr 1.2fr 0.8fr;padding:10px 12px;background:#f8fafc;border:1px solid #e5e7eb;border-radius:10px;font-size:12px;font-weight:700;color:#334155;margin-bottom:8px'>
            <div>任务标题</div><div>优先级</div><div>加入时间</div><div>状态</div>
        </div>
        """, unsafe_allow_html=True)
        for idx, item in enumerate(st.session_state.queue_items):
            status_options = ["待处理", "处理中", "已完成"]
            cols = st.columns([2,0.8,1.2,0.8])
            cols[0].markdown(item['title'])
            cols[1].markdown(item['priority'])
            cols[2].markdown(item['time'])
            new_status = cols[3].selectbox("状态", status_options, index=status_options.index(item['status']), key=f"queue_status_{idx}", label_visibility="collapsed")
            st.session_state.queue_items[idx]['status'] = new_status
    else:
        st.info("当前优化队列为空，点击上方“立即执行”后会进入列表。")

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
