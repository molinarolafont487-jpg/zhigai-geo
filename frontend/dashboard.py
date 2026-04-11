import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
import json
from pathlib import Path

st.set_page_config(page_title="智改GEO", layout="wide", page_icon="🧠")

# 深色专业主题
st.markdown("""
<style>
 .main { background-color: #0A0F1C; color: #E0E0E0; }
 .stMetric { background-color: #1A2338; border-radius: 12px; padding: 20px; }
 h1 { color: #00D4A5; font-weight: 700; }
 .stTabs [data-baseweb="tab-list"] button { color: #E0E0E0; }
 .stTabs [data-baseweb="tab-list"] button[aria-selected="true"] { color: #00D4A5; border-bottom: 3px solid #00D4A5; }
</style>
""", unsafe_allow_html=True)

st.title("🧠 智改GEO · SAGASAI.cc 豆包可见度监测")
st.caption("智改赋能深圳科技有限公司 | 让品牌被AI主动推荐")

# Sidebar
with st.sidebar:
    st.selectbox("品牌", ["SAGASAI.cc"], key="brand")
    st.selectbox("平台", ["豆包"], key="platform")
    st.selectbox("时间范围", ["最近7天", "最近30天"], key="time_range")

# 多 Tab
tab1, tab2, tab3, tab4, tab5 = st.tabs(["📊 总览", "📈 趋势分析", "💡 优化建议", "📋 监测记录", "🏆 竞品对比"])

with tab1:
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("可见度分数", "68.4", "↑14.2")
    with col2:
        st.metric("平均引用率", "58.3%", "↑12.4%")
    with col3:
        st.metric("正面情感比例", "76.5%", "↑8.2%")
    with col4:
        st.metric("需优化 Prompt", "7", "↓3")

    st.subheader("项目总览")
    st.info("当前页面为稳定化简版，保留核心监测能力与指标展示。")

    if st.button("🚀 开始真实豆包监测", type="primary"):
        st.info("正在调用豆包 API 进行监测...")

with tab2:
    st.subheader("7 天可见度趋势")
    dates = pd.date_range(end=datetime.now(), periods=7).tolist()
    visibility = [62, 65, 68, 72, 75, 80, 85]
    citation = [52, 55, 58, 60, 63, 65, 68]

    trend_df = pd.DataFrame({"日期": dates, "可见度分数": visibility, "平均引用率": citation})

    fig1 = px.line(trend_df, x="日期", y="可见度分数", markers=True, template="plotly_dark")
    fig1.update_traces(line_color="#00D4A5")
    st.plotly_chart(fig1, use_container_width=True)

    fig2 = px.line(trend_df, x="日期", y="平均引用率", markers=True, template="plotly_dark")
    fig2.update_traces(line_color="#3B82F6")
    st.plotly_chart(fig2, use_container_width=True)

with tab3:
    st.subheader("优化建议")
    st.warning("根据最新监测，建议优先加强以下内容：")
    st.markdown("""
 - 增加真实充值成功案例和截图
 - 补充支付成功率、到账时间等量化数据
 - 强化 FAQ 中资金安全与售后保障说明
 - 优化首页信任模块文案
 """)

with tab4:
    st.subheader("📋 历史监测记录")
    st.info("以下是过去监测的历史数据（自动从 monitor_results 文件夹读取）")

    history_dir = Path("/Users/yanlyubo/Desktop/zhigai-geo/monitor_results")

    if history_dir.exists():
        report_files = sorted(history_dir.glob("daily_report_*.md"), reverse=True)

        if report_files:
            selected_report = st.selectbox(
                "选择历史报告日期",
                options=[f.name for f in report_files],
                index=0
            )

            report_path = history_dir / selected_report
            with open(report_path, "r", encoding="utf-8") as f:
                report_content = f.read()

            st.markdown(report_content)

            st.subheader("最新监测摘要")
            try:
                report_stem = Path(selected_report).stem
                report_date = report_stem.replace("daily_report_", "")
                json_candidates = sorted(history_dir.glob(f"monitor_results_{report_date}*.json"), reverse=True)

                if not json_candidates:
                    raise FileNotFoundError(f"未找到 {report_date} 对应的 JSON 文件")

                with open(json_candidates[0], "r", encoding="utf-8") as f:
                    data = json.load(f)

                df = pd.DataFrame([
                    {
                        "Prompt": item.get("prompt", "N/A"),
                        "可见度": item.get("response", {}).get("visibility_score", "N/A"),
                        "是否推荐": item.get("response", {}).get("recommended", "N/A"),
                        "情感": item.get("response", {}).get("sentiment", "N/A")
                    }
                    for item in data
                ])
                st.dataframe(df, use_container_width=True)
            except Exception:
                st.info("详细 JSON 数据加载中...")
        else:
            st.info("暂无历史报告，请先运行一次监测。")
    else:
        st.info("monitor_results 文件夹不存在，请先运行一次监测生成数据。")

with tab5:
    st.subheader("🏆 竞品对比")
    st.info("在这里添加竞品网站，比较同一组 Prompt 下的可见度表现（Share of Voice）")

    col_a, col_b = st.columns(2)
    with col_a:
        competitor1 = st.text_input("竞品1", value="竞品平台A")
    with col_b:
        competitor2 = st.text_input("竞品2", value="竞品平台B")

    if st.button("开始竞品对比"):
        st.success("模拟对比结果（后续会接入真实数据）")
        compare_df = pd.DataFrame({
            "指标": ["平均可见度", "推荐率", "正面情感"],
            "SAGASAI.cc": ["85", "80%", "76%"],
            competitor1: ["72", "65%", "68%"],
            competitor2: ["68", "60%", "72%"]
        })
        st.dataframe(compare_df, use_container_width=True)

st.caption("智改GEO © 2026 智改赋能深圳科技有限公司 | 数据来源于豆包 Ark API")
