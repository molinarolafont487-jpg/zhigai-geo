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
    progress_bar = st.progress(0)
    status_box = st.empty()
    success_table = st.empty()
    failed_table = st.empty()

    success_rows: list[dict] = []
    failed_rows: list[dict] = []

    for idx, prompt in enumerate(prompts, start=1):
        status_box.info(f"正在监测第 {idx}/{total} 条... {prompt}")
        result = service.batch_monitor([prompt])[0]
        success_row, failed_row = parse_single_result(result)

        if success_row:
            success_rows.append(success_row)
            success_table.dataframe(pd.DataFrame(success_rows), use_container_width=True)
        if failed_row:
            failed_rows.append(failed_row)
            failed_table.dataframe(pd.DataFrame(failed_rows), use_container_width=True)

        progress_bar.progress(idx / total)

    status_box.success("渐进式批量真实豆包监测已完成")
    return success_rows, failed_rows


with st.sidebar:
    st.title("智改GEO")
    st.caption("智改赋能深圳科技有限公司")
    st.selectbox("品牌", ["SAGASAI.cc"])
    st.selectbox("平台", ["豆包"])
    st.selectbox("时间范围", ["最近7天", "最近30天"])

st.title("智改GEO · SAGASAI.cc 豆包可见度监测")
st.caption(f"更新时间：{datetime.now().strftime('%Y-%m-%d %H:%M')} | 第一租户演示")

col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("可见度分数", "68.4", "↑14.2")
with col2:
    st.metric("平均引用率", "58.3%", "↑12.4%")
with col3:
    st.metric("正面情感比例", "76.5%", "↑8.2%")
with col4:
    st.metric("需优化 Prompt", "7", "↓3")

tab1, tab2, tab3, tab4 = st.tabs(["总览", "优化建议", "监测记录", "说明"])

with tab1:
    st.subheader("项目总览")
    st.write("当前页面为稳定化简版，保留核心监测能力与指标展示。")
    summary = pd.DataFrame(
        [
            {"指标": "可见度分数", "值": "68.4"},
            {"指标": "平均引用率", "值": "58.3%"},
            {"指标": "正面情感比例", "值": "76.5%"},
            {"指标": "需优化 Prompt", "值": "7"},
        ]
    )
    st.dataframe(summary, use_container_width=True)

with tab2:
    st.subheader("真实豆包监测")
    st.write("点击下方按钮，执行渐进式批量真实监测。")
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
                "建议: 请检查 API Key、接入点 ID、网络，或查看后端日志。"
            )

with tab3:
    st.subheader("监测记录")
    records = pd.DataFrame(
        [
            {"Prompt": "国内怎么充值ChatGPT Plus 最简单方式", "引用率(%)": 85, "情感": "中性"},
            {"Prompt": "SAGASAI充值安全吗", "引用率(%)": 91, "情感": "中性"},
        ]
    )
    st.dataframe(records, use_container_width=True)

with tab4:
    st.subheader("部署说明")
    st.write("此版本已去除自定义 CSS 和复杂图表，优先保证 Streamlit Cloud 稳定加载。")

st.caption("智改GEO © 2026 智改赋能深圳科技有限公司")
