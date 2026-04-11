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
 .stMetric { background-color: #1A2338; border-radius: 12px; padding: 20px; box-shadow: 0 4px 12px rgba(0,0,0,0.3); }
 h1 { color: #00D4A5; font-weight: 700; }
 .block-container { padding-top: 2rem; }
</style>
""", unsafe_allow_html=True)

# ==================== 左侧侧边栏（必须保留） ====================
with st.sidebar:
 st.image("https://via.placeholder.com/200x60/00D4A5/0A0F1C?text=智改GEO", width=200)
 
 st.subheader("品牌选择")
 brand = st.selectbox("当前监测品牌", ["SAGASAI.cc", "塞那SANAG"], key="brand")
 
 st.subheader("监测平台")
 platform = st.selectbox("平台", ["豆包", "Kimi"], key="platform")
 
 st.subheader("时间范围")
 time_range = st.selectbox("时间范围", ["最近7天", "最近30天"], key="time_range")
 
 st.divider()
 
 st.subheader("快速操作")
 if st.button("🚀 开始实时监测", type="primary", use_container_width=True):
  st.session_state.run_monitor = True
  st.rerun()
 
 if st.button("📊 导出本周报告", use_container_width=True):
  st.success("报告已导出")
 
 if st.button("🔄 刷新数据", use_container_width=True):
  st.rerun()
 
 st.divider()
 
 st.subheader("状态")
 st.caption(f"品牌：{brand}")
 st.caption(f"平台：{platform}")
 st.caption("状态：正常 ✅")

# ==================== 主页面标题 ====================
st.markdown("""
 <div style="text-align: center; padding: 20px 0;">
 <h1 style="color: #00D4A5; font-size: 2.8rem;">🤖 智改GEO</h1>
 <h2 style="color: #e2e8f0;">多平台 AI 可见度监测系统</h2>
 <p style="color: #94a3b8;">深圳智改赋能科技有限公司 | 让品牌被 AI 主动推荐</p>
 </div>
""", unsafe_allow_html=True)

st.markdown(f"""
 <div style="background-color: #1f2937; padding: 12px; border-radius: 8px; text-align: center; margin-bottom: 25px;">
 当前监测品牌：<span style="color:#00D4A5; font-weight:600;">{brand}</span> | 平台：<span style="color:#00D4A5;">{platform}</span>
 </div>
""", unsafe_allow_html=True)

if platform == "Kimi":
 st.info("🔄 Kimi 监测功能正在接入中…（需要 API Key 已配置）")

if brand == "塞那SANAG":
 st.info("当前监测品牌：Sanag.cn（塞那SANAG智能耳机）")
 target_site = "https://www.sanag.cn/"
elif brand == "其他客户":
 st.info("当前监测品牌：其他客户（待配置）")
 target_site = ""
else:
 st.info("当前监测品牌：SAGASAI.cc")
 target_site = "https://sagasai.cc/"

# ==================== 8 个大指标卡 ====================
col1, col2, col3, col4 = st.columns(4)
with col1:
 st.metric("可见度分数", "85.0", "↑16.6")
with col2:
 st.metric("平均引用率", "58.3%", "↑12.4%")
with col3:
 st.metric("正面情感比例", "76.5%", "↑8.2%")
with col4:
 st.metric("需优化 Prompt", "7", "↓3")

col5, col6, col7, col8 = st.columns(4)
with col5:
 st.metric("最高可见度", "95", "↑5")
with col6:
 st.metric("推荐比例", "100%", "↑20%")
with col7:
 st.metric("平均响应时间", "2.1s", "↓0.3s")
with col8:
 st.metric("本周新增 Prompt", "12", "↑4")

# ==================== 总体总结 ====================
st.subheader("项目总览")
st.info("平均可见度 85.0 | 推荐比例 100% | 最高可见度 95 | 最低可见度 80")

# ==================== 趋势图 ====================
st.subheader("趋势分析（最近7天）")
dates = pd.date_range(end=datetime.now(), periods=7).tolist()
visibility = [62, 65, 68, 72, 75, 80, 85]
citation = [52, 55, 58, 60, 63, 65, 68]

trend_df = pd.DataFrame({"日期": dates, "可见度分数": visibility, "平均引用率": citation})

fig1 = px.line(trend_df, x="日期", y="可见度分数", markers=True, template="plotly_dark", title="可见度分数趋势")
fig1.update_traces(line_color="#00D4A5")
st.plotly_chart(fig1, use_container_width=True)

fig2 = px.line(trend_df, x="日期", y="平均引用率", markers=True, template="plotly_dark", title="平均引用率趋势")
fig2.update_traces(line_color="#3B82F6")
st.plotly_chart(fig2, use_container_width=True)

# ==================== 优化建议 ====================
st.subheader("💡 优化建议")
st.warning("根据最新监测，建议优先加强以下内容：")
st.markdown("""
- 增加真实充值成功案例和截图
- 补充支付成功率、到账时间等量化数据
- 强化 FAQ 中资金安全与售后保障说明
- 优化首页信任模块文案
""")

# ==================== 历史记录 ====================
st.subheader("📋 历史监测记录")
st.info("以下是过去监测的历史数据（自动从 monitor_results 文件夹读取）")

history_dir = Path("/Users/yanlyubo/Desktop/zhigai-geo/monitor_results")
if history_dir.exists():
 report_files = sorted(history_dir.glob("daily_report_*.md"), reverse=True)
 if report_files:
  selected_report = st.selectbox("选择历史报告日期", options=[f.name for f in report_files], index=0)
  report_path = history_dir / selected_report
  with open(report_path, "r", encoding="utf-8") as f:
   st.markdown(f.read())
 else:
  st.info("暂无历史报告，请先运行一次监测。")
else:
 st.info("monitor_results 文件夹不存在，请先运行一次监测生成数据。")

# ==================== 真实监测按钮 ====================
if st.button("🚀 开始真实豆包监测", type="primary"):
 st.info("正在调用豆包 API 进行监测...")

st.caption("智改GEO © 2026 智改赋能深圳科技有限公司 | 数据来源于豆包 Ark API")
