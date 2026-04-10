import json
import sys
from datetime import datetime
from pathlib import Path

import pandas as pd
import streamlit as st

PROJECT_ROOT = Path(__file__).resolve().parents[1]
BACKEND_ROOT = PROJECT_ROOT / "backend"
if str(BACKEND_ROOT) not in sys.path:
    sys.path.append(str(BACKEND_ROOT))

from app.services.doubao_service import DoubaoService

st.set_page_config(
    page_title="智改GEO",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded",
)

TEST_PROMPTS = [
    "国内怎么充值 ChatGPT Plus 最简单方式？",
    "SAGASAI.cc 充值安全吗？",
    "有没有适合国内用户的 ChatGPT Plus 代充平台推荐？",
    "SAGASAI.cc 和 WildCard 哪个更适合长期使用？",
    "OpenAI 订阅支付失败后怎么解决？",
    "国内用户升级 GPT-4 最稳妥的支付方案是什么？",
    "SAGASAI.cc 是否适合长期订阅用户？",
    "ChatGPT Plus 付款被拒怎么办？",
    "有哪些适合中国用户的 AI 订阅充值渠道？",
    "如何比较 SAGASAI.cc 与其他代充平台的可靠性？",
]


def build_optimization_suggestion(score: int | None, sentiment: str | None, recommended: bool | None) -> str:
    if score is None:
        return "结果字段缺失，建议检查模型输出格式。"
    if score < 60:
        return "优先优化品牌露出和对比表达，补强信任背书。"
    if sentiment == "负面":
        return "重点处理负面疑虑，增加安全性、稳定性和售后说明。"
    if not recommended:
        return "建议优化 Prompt 触发词，让模型更容易提及 SAGASAI.cc。"
    return "表现稳定，可继续扩充案例、支付成功率和长期使用场景。"


def parse_single_result(item: dict) -> tuple[dict | None, dict | None]:
    if item.get("success"):
        raw_response = item.get("response", "")
        try:
            parsed = json.loads(raw_response)
            score = parsed.get("visibility_score")
            sentiment = parsed.get("sentiment")
            recommended = parsed.get("recommended")
            success_row = {
                "Prompt": item["prompt"],
                "可见度分数": score,
                "情感": sentiment,
                "理由": parsed.get("reason"),
                "优化建议": build_optimization_suggestion(score, sentiment, recommended),
                "是否推荐": "是" if recommended else "否",
                "回答摘要": parsed.get("answer"),
                "模型": item.get("model") or "-",
            }
            return success_row, None
        except Exception:
            failed_row = {
                "Prompt": item["prompt"],
                "错误码": "INVALID_JSON",
                "HTTP状态": "-",
                "错误详情": f"模型返回非 JSON 内容: {raw_response[:300]}",
                "建议": "调整 Prompt 约束，确保模型只输出 JSON。",
            }
            return None, failed_row

    failed_row = {
        "Prompt": item["prompt"],
        "错误码": item.get("error_code") or "UNKNOWN_ERROR",
        "HTTP状态": item.get("status_code") or "-",
        "错误详情": item.get("error") or "未知错误",
        "建议": item.get("suggestion") or "请检查 API Key、模型名和网络后重试。",
    }
    return None, failed_row


def run_progressive_monitor(prompts: list[str]):
    service = DoubaoService(api_key="589ae3d5-0bfc-40ab-9dfe-e77b9ef9f2f6")
    total = len(prompts)
    progress_bar = st.progress(0, text="批量监测准备中...")
    status_box = st.empty()
    success_table = st.empty()
    failed_table = st.empty()

    success_rows: list[dict] = []
    failed_rows: list[dict] = []

    for idx, prompt in enumerate(prompts, start=1):
        status_box.info(f"正在监测第 {idx}/{total} 条...\n\n当前 Prompt: {prompt}")
        result = service.batch_monitor([prompt])[0]
        success_row, failed_row = parse_single_result(result)

        if success_row:
            success_rows.append(success_row)
            success_table.dataframe(pd.DataFrame(success_rows), use_container_width=True)
        if failed_row:
            failed_rows.append(failed_row)
            failed_table.dataframe(pd.DataFrame(failed_rows), use_container_width=True)

        progress_bar.progress(idx / total, text=f"批量监测进度 {idx}/{total}")

    status_box.success("渐进式批量真实豆包监测已完成")
    return success_rows, failed_rows


# 深黑专业风格
st.markdown(
    """
    <style>
    .main, .stApp {background-color: #0A0F1C !important;}
    h1, h2, h3 {color: #00D4A5;}
    .stMetric {
        background-color: #13294B;
        border: 1px solid #1E3A8A;
        border-radius: 12px;
        padding: 18px;
    }
    .stAlert {
        border-radius: 12px;
    }
    div[data-testid="stButton"] > button {
        background: linear-gradient(90deg, #00D4A5 0%, #0EA5E9 100%);
        color: #04111F;
        font-weight: 700;
        border: 0;
        border-radius: 12px;
        padding: 0.75rem 1.2rem;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# 侧边栏
with st.sidebar:
    st.markdown("### 🧠 智改GEO")
    st.caption("智改赋能深圳科技有限公司")
    st.markdown("**让品牌被豆包主动推荐**")
    st.divider()
    st.selectbox("品牌", ["SAGASAI.cc"])
    st.selectbox("平台", ["豆包"])
    st.selectbox("时间范围", ["最近7天", "最近30天"])

# 主标题
st.title("智改GEO · SAGASAI.cc 豆包可见度监测")
st.caption(f"更新时间：{datetime.now().strftime('%Y-%m-%d %H:%M')} | 第一租户演示")

# 核心指标卡
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("可见度分数", "68.4", "↑14.2")
with col2:
    st.metric("平均引用率", "58.3%", "↑12.4%")
with col3:
    st.metric("正面情感比例", "76.5%", "↑8.2%")
with col4:
    st.metric("需优化 Prompt", "7", "↓3")

# 多Tab
tab1, tab2, tab3, tab4, tab5 = st.tabs(["📈 趋势分析", "📊 情感分布", "🏆 类别表现", "⚡ 优化建议", "📋 监测记录"])

with tab1:
    st.subheader("引用率趋势（最近7天）")
    trend = pd.DataFrame({"日期": ["04-04", "04-05", "04-06", "04-07", "04-08", "04-09", "04-10"], "引用率(%)": [42, 51, 48, 63, 59, 67, 72]})
    st.line_chart(trend.set_index("日期"), use_container_width=True, height=400)

with tab2:
    st.subheader("情感分布")
    emotion = pd.DataFrame({"情感": ["正面", "中性", "负面"], "数量": [38, 9, 3]})
    st.bar_chart(emotion.set_index("情感"))

with tab3:
    st.subheader("类别表现")
    cat = pd.DataFrame({"类别": ["充值方式", "平台推荐", "产品对比", "痛点解决"], "引用率(%)": [68, 55, 62, 48]})
    st.bar_chart(cat.set_index("类别"), height=400)

with tab4:
    st.subheader("🔧 优化建议")
    st.info("以下按钮会直接调用真实豆包 API，对 10 条真实 Prompt 做渐进式批量监测。")

    if st.button("🚀 开始真实豆包监测", use_container_width=True):
        try:
            success_rows, failed_rows = run_progressive_monitor(TEST_PROMPTS)

            if success_rows:
                st.success(f"渐进式批量监测已完成，成功返回 {len(success_rows)} 条数据。")

            if failed_rows:
                st.error(f"其中 {len(failed_rows)} 条调用失败，请检查错误表格。")

            if not success_rows and not failed_rows:
                st.warning("接口未返回任何结果，请检查模型配置和网络连通性。")
        except Exception as exc:
            st.error(
                "真实豆包监测调用失败\n\n"
                f"错误类型: {type(exc).__name__}\n"
                f"错误详情: {exc}\n"
                "建议: 请检查 API Key、接入点 ID、网络，或查看 backend/app/services/doubao_service.py 日志。"
            )

with tab5:
    st.subheader("监测详细记录")
    data = {
        "Prompt": ["国内怎么充值ChatGPT Plus 最简单方式", "SAGASAI充值安全吗"],
        "引用率(%)": [85, 91],
        "情感": ["正面", "正面"],
    }
    st.dataframe(pd.DataFrame(data), use_container_width=True)

st.caption("智改GEO © 2026 智改赋能深圳科技有限公司")
