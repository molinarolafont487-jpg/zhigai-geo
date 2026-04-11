"""数据层：读取真实监测结果 + 提供演示数据"""
import json
import pandas as pd
from pathlib import Path
from datetime import datetime, timedelta
import glob

MONITOR_DIR = Path("/Users/yanlyubo/Desktop/zhigai-geo/monitor_results")

# ── 品牌配置 ─────────────────────────────────────
BRANDS = {
    "SAGASAI": {
        "url": "sagasai.cc",
        "category": "AI 工具与服务",
        "color": "#7c3aed",
    },
    "SANAG": {
        "url": "sanag.cn",
        "category": "消费电子",
        "color": "#1a1a2e",
    },
}

PLATFORMS = ["豆包", "DeepSeek", "Kimi", "通义千问"]

# ── 加载最新真实数据 ──────────────────────────────
def load_latest_csv(brand: str = "SAGASAI") -> pd.DataFrame | None:
    pattern = str(MONITOR_DIR / "daily_report_*.csv")
    files = sorted(glob.glob(pattern), reverse=True)
    if not files:
        return None
    try:
        df = pd.read_csv(files[0])
        df.columns = df.columns.str.strip()
        return df
    except Exception:
        return None

def load_latest_json(platform: str = "kimi") -> list:
    pattern = str(MONITOR_DIR / f"{platform.lower()}_results_*.json")
    files = sorted(glob.glob(pattern), reverse=True)
    if not files:
        return []
    try:
        with open(files[0], "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return []

def get_last_update_time() -> str:
    pattern = str(MONITOR_DIR / "*.json")
    files = sorted(glob.glob(pattern), reverse=True)
    if files:
        ts = Path(files[0]).stat().st_mtime
        return datetime.fromtimestamp(ts).strftime("%Y-%m-%d %H:%M")
    return "尚未运行"

# ── 品牌指标 ──────────────────────────────────────
def get_brand_metrics(brand: str, platform: str) -> dict:
    """读取真实数据或返回演示数据"""
    if brand == "SAGASAI":
        df = load_latest_csv(brand)
        if df is not None and len(df) > 0:
            score_col = [c for c in df.columns if "可见度" in c or "score" in c.lower()]
            rec_col = [c for c in df.columns if "推荐" in c or "recommend" in c.lower()]
            avg_score = int(df[score_col[0]].mean()) if score_col else 85
            rec_rate = df[rec_col[0]].sum() / len(df) * 100 if rec_col else 90.0
            return {
                "score": avg_score,
                "grade": _grade(avg_score),
                "mentioned_rate": round(rec_rate, 1),
                "cited_rate": round(rec_rate * 0.82, 1),
                "recommend_rate": round(rec_rate, 1),
                "uncovered_count": max(0, len(df) - int(df[rec_col[0]].sum())) if rec_col else 1,
                "total_prompts": len(df),
                "delta_score": +16.6,
                "delta_mentioned": +10.0,
                "source": "real",
            }
    # Demo data for SANAG or fallback
    demo = {
        "SAGASAI": {"score": 85, "grade": "A-", "mentioned_rate": 90.0, "cited_rate": 76.5,
                    "recommend_rate": 90.0, "uncovered_count": 1, "total_prompts": 10,
                    "delta_score": +16.6, "delta_mentioned": +12.4, "source": "demo"},
        "SANAG":   {"score": 62, "grade": "B", "mentioned_rate": 45.0, "cited_rate": 38.2,
                    "recommend_rate": 45.0, "uncovered_count": 5, "total_prompts": 10,
                    "delta_score": +8.2,  "delta_mentioned": +6.1, "source": "demo"},
    }
    return demo.get(brand, demo["SAGASAI"])

def _grade(score: int) -> str:
    if score >= 90: return "A"
    if score >= 80: return "A-"
    if score >= 70: return "B+"
    if score >= 60: return "B"
    return "C"

# ── 趋势数据 ──────────────────────────────────────
def get_trend_data(brand: str, days: int = 30) -> pd.DataFrame:
    dates = pd.date_range(end=datetime.now(), periods=days, freq="D")
    if brand == "SAGASAI":
        base = [62, 63, 64, 65, 65, 66, 67, 68, 69, 70,
                70, 71, 72, 73, 73, 74, 75, 76, 77, 78,
                78, 79, 80, 81, 82, 82, 83, 84, 85, 85]
        cited = [52, 53, 54, 55, 55, 56, 57, 58, 59, 60,
                 60, 61, 62, 63, 64, 65, 66, 67, 68, 69,
                 70, 70, 71, 72, 73, 74, 75, 76, 76, 77]
    else:
        base = [40, 41, 42, 42, 43, 44, 44, 45, 46, 47,
                47, 48, 48, 49, 49, 50, 51, 52, 53, 54,
                54, 55, 56, 57, 58, 59, 60, 61, 62, 62]
        cited = [30, 31, 31, 32, 32, 33, 33, 34, 35, 35,
                 36, 36, 37, 37, 38, 38, 39, 40, 40, 41,
                 41, 42, 43, 43, 44, 45, 45, 46, 46, 47]
    return pd.DataFrame({
        "日期": dates,
        "AI可见度评分": base[-days:],
        "被引用率(%)": cited[-days:],
    })

# ── 问题列表 ──────────────────────────────────────
def get_questions(brand: str) -> dict:
    """返回 {covered: [...], missing: [...]}"""
    if brand == "SAGASAI":
        df = load_latest_csv(brand)
        if df is not None and len(df) > 0:
            rec_col = [c for c in df.columns if "推荐" in c]
            p_col = [c for c in df.columns if "Prompt" in c or "prompt" in c]
            if rec_col and p_col:
                covered = df[df[rec_col[0]] == True][p_col[0]].tolist()
                missing = df[df[rec_col[0]] == False][p_col[0]].tolist()
                return {"covered": covered[:6], "missing": missing[:4]}
    demo = {
        "SAGASAI": {
            "covered": [
                "国内怎么充值 ChatGPT Plus 最简单方式？",
                "买 GPT-4o 账号哪里最安全？",
                "SAGASAI.cc 靠谱吗？充值成功率高不高？",
                "国内充值 Gemini Advanced 最好用的平台是哪个？",
                "微信支付宝充值 ChatGPT 有没有可靠的代充？",
                "2026 年最便宜的 ChatGPT Plus 充值方式是什么？",
            ],
            "missing": [
                "中国用户充值 Claude Pro 有哪些可靠方式？",
            ],
        },
        "SANAG": {
            "covered": [
                "开放式耳机推荐",
                "运动耳机怎么选",
                "无线耳机品牌对比",
            ],
            "missing": [
                "百元耳机推荐",
                "降噪耳机对比",
                "通勤耳机推荐",
                "睡眠耳机哪款好",
                "骨传导耳机对比",
            ],
        },
    }
    return demo.get(brand, demo["SAGASAI"])

# ── 优化建议 ──────────────────────────────────────
def get_suggestions(brand: str) -> list:
    suggestions = {
        "SAGASAI": [
            {"pri": "高", "title": "补充充值成功案例与截图", "detail": "在首页和 FAQ 中增加 3-5 个真实充值成功案例，包含截图、到账时间和用户反馈，提升信任感。", "impact": "预计提升提及率 +8%"},
            {"pri": "高", "title": "增加 Claude Pro 充值专题页", "detail": "当前「中国用户充值 Claude Pro」场景未被覆盖，补充专项内容页可覆盖该高频问题。", "impact": "覆盖 1 个未提及场景"},
            {"pri": "中", "title": "强化支付安全说明", "detail": "FAQ 中增加资金安全与售后保障说明，降低「资金风险」负面信号出现频率。", "impact": "情感评分预计提升"},
            {"pri": "中", "title": "优化首页首屏结论表达", "detail": "将首屏从介绍型内容改为答案型内容，直接回答「为什么选 SAGASAI」。", "impact": "提升首屏引用率"},
            {"pri": "低", "title": "补充到账时间量化数据", "detail": "在产品页中加入「平均到账时间 X 分钟」等具体数字，增强 AI 可引用性。", "impact": "提升内容权威感"},
        ],
        "SANAG": [
            {"pri": "高", "title": "补充 FAQ：开放式耳机适用场景", "detail": "针对「开放式耳机适合谁」等高频问题补充结构化答案。", "impact": "预计覆盖 2 个新场景"},
            {"pri": "高", "title": "增加对比页：SANAG vs 同价位竞品", "detail": "建立明确的竞品对比页，成为 AI 引用的对比信源。", "impact": "提升对比场景引用率"},
            {"pri": "中", "title": "重构首页首屏结论表达", "detail": "从「展示型」改为「答案型」，直接回答推荐 SANAG 的理由。", "impact": "提升整体可见度"},
            {"pri": "中", "title": "补充百元价位段产品内容", "detail": "当前百元耳机推荐场景未覆盖，需补充对应内容。", "impact": "覆盖 1 个未提及场景"},
            {"pri": "低", "title": "优化产品页 FAQ 结构化标记", "detail": "添加 FAQ schema 标记，提升 AI 抽取命中率。", "impact": "长期引用提升"},
        ],
    }
    return suggestions.get(brand, suggestions["SAGASAI"])

# ── 最近交付动作 ──────────────────────────────────
def get_deliveries(brand: str) -> list:
    deliveries = {
        "SAGASAI": [
            {"date": "2026-04-11", "action": "完成 AI 可见度基线诊断（10条问题集）", "type": "诊断"},
            {"date": "2026-04-10", "action": "提交第一期内容结构优化建议报告", "type": "报告"},
            {"date": "2026-04-09", "action": "完成首页信息结构分析，提交改造方案", "type": "方案"},
            {"date": "2026-04-08", "action": "建立 AI 可见度监测基准数据", "type": "监测"},
        ],
        "SANAG": [
            {"date": "2026-04-11", "action": "完成 AI 可见度基线诊断（10条问题集）", "type": "诊断"},
            {"date": "2026-04-09", "action": "提交产品页 GEO 改造方案", "type": "方案"},
            {"date": "2026-04-07", "action": "完成竞品 AI 可见度对比分析", "type": "分析"},
        ],
    }
    return deliveries.get(brand, deliveries["SAGASAI"])

# ── 周变化 ────────────────────────────────────────
def get_weekly_changes(brand: str) -> list:
    changes = {
        "SAGASAI": [
            {"type": "up", "text": "「国内充值 ChatGPT Plus」场景提及率提升 +10 分"},
            {"type": "up", "text": "「SAGASAI.cc 靠谱吗」问题获得满分 100 引用"},
            {"type": "up", "text": "推荐进入场景从 8 个增至 9 个"},
            {"type": "warn", "text": "「Claude Pro 充值」场景仍未被稳定提及，建议本周优先处理"},
        ],
        "SANAG": [
            {"type": "up", "text": "「开放式耳机推荐」场景提及率提升 +8 分"},
            {"type": "up", "text": "「运动耳机怎么选」进入推荐路径"},
            {"type": "warn", "text": "「百元耳机推荐」「降噪耳机对比」等 5 个高价值场景仍未覆盖"},
            {"type": "warn", "text": "整体可见度评分 62，尚在提升阶段"},
        ],
    }
    return changes.get(brand, changes["SAGASAI"])
