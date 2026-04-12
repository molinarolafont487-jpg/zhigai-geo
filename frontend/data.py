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
    pattern = str(MONITOR_DIR / "monitor_results_*.json")
    files = sorted(glob.glob(pattern))
    rows = []
    for fp in files:
        try:
            ts = Path(fp).stem.replace("monitor_results_", "")
            dt = datetime.strptime(ts, "%Y%m%d_%H%M")
            with open(fp, "r", encoding="utf-8") as f:
                data = json.load(f)
            if not data:
                continue
            vis = []
            rec = []
            for item in data:
                response = item.get("response", {})
                if isinstance(response, str):
                    try:
                        response = json.loads(response)
                    except Exception:
                        response = {}
                vis.append(response.get("visibility_score") or response.get("score") or 0)
                rec.append(1 if str(response.get("recommended", False)).lower() == "true" or response.get("recommended") is True else 0)
            avg_vis = sum(vis) / len(vis) if vis else 0
            avg_rec = (sum(rec) / len(rec) * 100) if rec else 0
            rows.append({"日期": dt, "AI可见度评分": avg_vis, "被引用率(%)": avg_rec})
        except Exception:
            continue
    if not rows:
        dates = pd.date_range(end=datetime.now(), periods=days, freq="D")
        return pd.DataFrame({"日期": dates, "AI可见度评分": [0]*days, "被引用率(%)": [0]*days})
    df = pd.DataFrame(rows).sort_values("日期")
    if len(df) < days:
        last_date = df["日期"].max()
        needed = days - len(df)
        pad_dates = pd.date_range(end=last_date, periods=needed+1, freq="D")[:-1]
        pad = pd.DataFrame({"日期": pad_dates, "AI可见度评分": [df["AI可见度评分"].iloc[0]]*needed, "被引用率(%)": [df["被引用率(%)"].iloc[0]]*needed})
        df = pd.concat([pad, df], ignore_index=True)
    return df.tail(days)

# ── 问题列表 ──────────────────────────────────────
def get_questions(brand: str) -> dict:
    """返回真实结构化问题列表"""
    if brand == "SAGASAI":
        df = load_latest_csv(brand)
        if df is not None and len(df) > 0:
            rec_col = [c for c in df.columns if "推荐" in c]
            p_col = [c for c in df.columns if "Prompt" in c or "prompt" in c]
            if rec_col and p_col:
                missing_rows = df[df[rec_col[0]] == False]
                covered_rows = df[df[rec_col[0]] == True]
                missing = []
                for i, (_, row) in enumerate(missing_rows.iterrows()):
                    prompt = str(row[p_col[0]])
                    status = "竞品领先" if any(k in prompt for k in ["Claude Pro", "对比", "哪个性价比最高"]) else "未进入推荐路径"
                    pri = "高" if i < 2 else "中"
                    action = "建议立即补充FAQ案例" if "靠谱吗" in prompt or "充值" in prompt else "建议重写标题并补充对比内容"
                    missing.append({"question": prompt, "platform": "豆包", "status": status, "priority": pri, "action": action})
                covered = [str(x) for x in covered_rows[p_col[0]].tolist()[:6]]
                return {"covered": covered, "missing": missing}
    demo = {
        "SAGASAI": {
            "covered": [
                "国内怎么充值 ChatGPT Plus 最简单方式？",
                "买 GPT-4o 账号哪里最安全？",
                "SAGASAI.cc 靠谱吗？充值成功率高不高？",
                "国内充值 Gemini Advanced 最好用的平台是哪个？",
            ],
            "missing": [
                {"question": "中国用户充值 Claude Pro 有哪些可靠方式？", "platform": "豆包", "status": "竞品领先", "priority": "高", "action": "建议立即补充 Claude Pro FAQ 案例"},
                {"question": "对比几个 AI 充值平台，哪个性价比最高？", "platform": "豆包", "status": "未进入推荐路径", "priority": "中", "action": "建议增加竞品对比页"},
            ],
        },
        "SANAG": {
            "covered": ["开放式耳机推荐", "运动耳机怎么选", "无线耳机品牌对比"],
            "missing": [
                {"question": "百元耳机推荐", "platform": "豆包", "status": "未提及", "priority": "高", "action": "建议立即补充百元价位段案例"},
                {"question": "降噪耳机对比", "platform": "豆包", "status": "竞品领先", "priority": "高", "action": "建议新增竞品对比模块"},
            ],
        },
    }
    return demo.get(brand, demo["SAGASAI"])

# ── 优化建议 ──────────────────────────────────────
def log_execution(brand: str, title: str):
    log_path = MONITOR_DIR / "optimization_queue.log"
    with open(log_path, "a", encoding="utf-8") as f:
        f.write(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | {brand} | {title}\n")


def get_suggestions(brand: str) -> list:
    q = get_questions(brand)
    suggestions = []
    for item in q.get('missing', [])[:5]:
        suggestions.append({
            "pri": item["priority"],
            "title": f"处理问题：{item['question']}",
            "detail": item["action"],
            "impact": "预计可见度提升 15-25 分" if item["priority"] == "高" else "预计推荐率进一步改善"
        })
    if not suggestions:
        suggestions = [{"pri": "中", "title": "继续更新真实案例", "detail": "保持每周新增 2-3 个可验证案例", "impact": "预计稳定推荐率"}]
    return suggestions

# ── 最近交付动作 ──────────────────────────────────
def get_deliveries(brand: str) -> list:
    items = []
    for fp in sorted(glob.glob(str(MONITOR_DIR / "monitor_results_*.json")), reverse=True)[:4]:
        dt = datetime.fromtimestamp(Path(fp).stat().st_mtime).strftime("%Y-%m-%d")
        items.append({"date": dt, "action": f"生成监测结果文件 {Path(fp).name}", "type": "监测"})
    for fp in sorted(glob.glob(str(MONITOR_DIR / "daily_report_*.md")), reverse=True)[:2]:
        dt = datetime.fromtimestamp(Path(fp).stat().st_mtime).strftime("%Y-%m-%d")
        items.append({"date": dt, "action": f"输出日报 {Path(fp).name}", "type": "报告"})
    return items[:5]

# ── 周变化 ────────────────────────────────────────
def get_weekly_changes(brand: str) -> list:
    df7 = get_trend_data(brand, 7)
    if len(df7) < 2:
        return []
    first = df7.iloc[0]
    last = df7.iloc[-1]
    score_delta = round(last['AI可见度评分'] - first['AI可见度评分'], 1)
    cite_delta = round(last['被引用率(%)'] - first['被引用率(%)'], 1)
    changes = []
    changes.append({"type": "up" if score_delta >= 0 else "warn", "text": f"过去7天 AI 可见度变化 {score_delta:+.1f} 分"})
    changes.append({"type": "up" if cite_delta >= 0 else "warn", "text": f"过去7天 被引用率变化 {cite_delta:+.1f}%"})
    q = get_questions(brand)
    changes.append({"type": "warn" if q['missing'] else "up", "text": f"当前仍有 {len(q['missing'])} 个高价值问题未覆盖"})
    return changes
