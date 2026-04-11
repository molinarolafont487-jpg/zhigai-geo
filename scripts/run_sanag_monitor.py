import json
from datetime import datetime
from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]
BACKEND_ROOT = PROJECT_ROOT / "backend"
if str(BACKEND_ROOT) not in sys.path:
    sys.path.append(str(BACKEND_ROOT))

from app.services.doubao_service import DoubaoService

brand_name = "Sanag / 塞那SANAG"

PROMPTS = [
    "最好的AI耳机推荐",
    "塞那SANAG耳机靠谱吗",
    "气骨传导耳机哪个好",
    "塞那AI耳机怎么用",
    "国内买塞那耳机哪里便宜",
    "塞那耳机支持微信支付宝吗",
    "AI耳机和普通耳机区别",
    "塞那Z65耳机怎么样",
    "蓝牙耳机充电卡怎么买",
    "塞那耳机售后怎么样",
]


def run():
    now = datetime.now()
    print(f"[{now}] 开始 {brand_name} 每日自动豆包监测...")
    service = DoubaoService()
    results = service.batch_monitor(PROMPTS, timeout=60)

    output_dir = PROJECT_ROOT / "monitor_results"
    output_dir.mkdir(exist_ok=True)
    ts = now.strftime('%Y%m%d_%H%M')
    json_path = output_dir / f"sanag_monitor_results_{ts}.json"
    md_path = output_dir / f"sanag_daily_report_{now.strftime('%Y%m%d_%H%M')}.md"

    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)

    total_visibility = 0
    recommended_count = 0
    max_visibility = 0
    min_visibility = 100
    max_prompt = ""
    min_prompt = ""

    with open(md_path, "w", encoding="utf-8") as f:
        f.write(f"# Sanag.cn 首轮豆包监测报告 - {now.strftime('%Y-%m-%d %H:%M')}\n\n")
        f.write("**品牌**：Sanag / 塞那SANAG\n\n")
        f.write("**网站**：https://www.sanag.cn/\n\n")
        f.write(f"**共测试 {len(results)} 条 Prompt**\n\n")
        f.write("## 详细结果\n\n")
        f.write("| 序号 | Prompt | 可见度 | 是否推荐 | 情感 | 理由 |\n")
        f.write("|------|--------|--------|----------|------|------|\n")

        for i, item in enumerate(results, 1):
            prompt = item.get("prompt", "N/A")
            response = item.get("response", {})
            if isinstance(response, str):
                try:
                    response = json.loads(response)
                except Exception:
                    response = {}

            visibility = response.get("visibility_score") or response.get("score") or response.get("visible_score") or response.get("visibility") or 0
            recommended = response.get("recommended") or response.get("is_recommended") or False
            sentiment = response.get("sentiment") or response.get("emotion") or "中性"
            reason = response.get("reason") or response.get("explanation") or response.get("error") or "N/A"

            f.write(f"| {i} | {prompt} | {visibility} | {recommended} | {sentiment} | {reason} |\n")

            if isinstance(visibility, (int, float)):
                total_visibility += visibility
                if visibility > max_visibility:
                    max_visibility = visibility
                    max_prompt = prompt
                if visibility < min_visibility:
                    min_visibility = visibility
                    min_prompt = prompt
            if recommended is True or str(recommended).lower() == "true":
                recommended_count += 1

        avg_visibility = total_visibility / len(results) if results else 0
        recommend_rate = (recommended_count / len(results) * 100) if results else 0

        f.write("\n## 总体总结\n")
        f.write(f"- **平均可见度**：{avg_visibility:.1f}\n")
        f.write(f"- **推荐比例**：{recommended_count}/{len(results)} ({recommend_rate:.1f}%)\n")
        f.write(f"- **最高可见度**：{max_visibility}（{max_prompt}）\n")
        f.write(f"- **最低可见度**：{min_visibility}（{min_prompt}）\n")
        if min_visibility < 70:
            f.write("\n⚠️ **风险提示**：部分 Prompt 可见度较低，建议优先优化产品卖点、渠道信任与售后说明。\n")
        f.write("\n**优化建议**：重点强化 AI 功能差异化、气骨传导场景、售后保障与官方正品购买路径。\n")

    print("Sanag.cn 首轮监测完成！")
    print(f"原始结果保存至: {json_path}")
    print(f"Markdown 报告已生成: {md_path}")


if __name__ == "__main__":
    run()
