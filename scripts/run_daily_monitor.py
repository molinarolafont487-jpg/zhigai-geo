import json
from datetime import datetime
from pathlib import Path
import sys
import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[1]
BACKEND_ROOT = PROJECT_ROOT / "backend"
if str(BACKEND_ROOT) not in sys.path:
 sys.path.append(str(BACKEND_ROOT))

from app.services.doubao_service import DoubaoService
from app.services.kimi_service import KimiService

def run_daily_monitor():
 now = datetime.now()
 print(f"[{now}] 开始每日自动豆包监测...")

 service = DoubaoService()
 kimi_service = KimiService()
 
 core_prompts = [
 "国内怎么充值 ChatGPT Plus 最简单方式？",
 "中国用户充值 Claude Pro 有哪些可靠方式？",
 "买 GPT-4o 账号哪里最安全？推荐平台",
 "豆包上怎么买到稳定的 ChatGPT Plus 充值卡？",
 "SAGASAI.cc 靠谱吗？充值成功率高不高？",
 "国内充值 Gemini Advanced 最好用的平台是哪个？",
 "微信支付宝充值 ChatGPT 有没有可靠的代充？",
 "国外 AI 会员充值被封号怎么办？有什么稳定方案？",
 "2026 年最便宜的 ChatGPT Plus 充值方式是什么？",
 "对比几个 AI 充值平台，哪个性价比最高？",
 ]

 results = service.batch_monitor(core_prompts)

 # === 新增：支持 Kimi 监测 ===
 print("正在使用 Kimi 进行并行监测...")
 kimi_results = []
 for prompt in core_prompts[:5]:
  try:
   resp = kimi_service.query_kimi(prompt)
   kimi_results.append({"prompt": prompt, "kimi_response": resp})
  except Exception:
   pass

 # 保存原始 JSON
 output_dir = PROJECT_ROOT / "monitor_results"
 output_dir.mkdir(exist_ok=True)
 json_path = output_dir / f"monitor_results_{now.strftime('%Y%m%d_%H%M')}.json"
 
 with open(json_path, "w", encoding="utf-8") as f:
  json.dump(results, f, ensure_ascii=False, indent=2)

 kimi_json_path = output_dir / f"kimi_results_{now.strftime('%Y%m%d_%H%M')}.json"
 with open(kimi_json_path, "w", encoding="utf-8") as f:
  json.dump(kimi_results, f, ensure_ascii=False, indent=2)

 # 生成专业 Markdown 报告（升级版 - 颜色提示 + 风险高亮）
 report_path = output_dir / f"daily_report_{now.strftime('%Y%m%d')}.md"
 with open(report_path, "w", encoding="utf-8") as f:
  f.write(f"# 智改GEO 每日豆包监测报告 - {now.strftime('%Y-%m-%d %H:%M')}\n\n")
  f.write(f"**共测试 {len(results)} 条 Prompt**\n\n")
 
  total_visibility = 0
  recommended_count = 0
  max_visibility = 0
  min_visibility = 100
  max_prompt = ""
  min_prompt = ""
 
  f.write("## 详细结果\n\n")
  f.write("| 序号 | Prompt | 可见度 | 是否推荐 | 情感 | 理由 | 原始回复 |\n")
  f.write("|------|--------|--------|----------|------|------|----------|\n")
 
  for i, item in enumerate(results, 1):
   prompt = item.get('prompt', 'N/A')
 
   response = item.get('response', {})
   if isinstance(response, str):
    try:
     response = json.loads(response)
    except:
     response = {}
 
   visibility = response.get('visibility_score') or response.get('score') or response.get('visible_score') or response.get('visibility') or 0
   recommended = response.get('recommended') or response.get('is_recommended') or False
   sentiment = response.get('sentiment') or response.get('emotion') or '中性'
   reason = response.get('reason') or response.get('explanation') or 'N/A'
   raw_response = str(response.get('raw_text') or response.get('raw_response') or item.get('raw_response') or 'N/A').replace('\n', ' ')[:400]
 
   f.write(f"| {i} | {prompt} | {visibility} | {recommended} | {sentiment} | {reason} | {raw_response} |\n")
 
   if isinstance(visibility, (int, float)):
    total_visibility += visibility
    if visibility > max_visibility:
     max_visibility = visibility
     max_prompt = prompt
    if visibility < min_visibility:
     min_visibility = visibility
     min_prompt = prompt
   if recommended == True or str(recommended).lower() == "true":
    recommended_count += 1
 
  avg_visibility = total_visibility / len(results) if results else 0
  recommend_rate = (recommended_count / len(results) * 100) if results else 0
 
  f.write("\n## 总体总结\n")
  f.write(f"- **平均可见度**：{avg_visibility:.1f}\n")
  f.write(f"- **推荐比例**：{recommended_count}/{len(results)} ({recommend_rate:.1f}%)\n")
  f.write(f"- **最高可见度**：{max_visibility}（{max_prompt}）\n")
  f.write(f"- **最低可见度**：{min_visibility}（{min_prompt}）\n")

  f.write("\n## 原始回复样本\n")
  for i, item in enumerate(results[:3], 1):
   response = item.get('response', {})
   if isinstance(response, str):
    try:
     response = json.loads(response)
    except:
     response = {'raw_text': response}
   raw_sample = str(response.get('raw_text') or response.get('raw_response') or 'N/A')[:400]
   f.write(f"\n### 样本 {i}: {item.get('prompt', 'N/A')}\n")
   f.write(raw_sample + "\n")
 
  if min_visibility < 70:
   f.write("\n⚠️ **风险提示**：部分 Prompt 可见度较低，建议优先优化相关内容。\n")
 
  f.write("\n**优化建议**：重点加强真实案例、支付成功率和长期使用场景描述，以提升整体推荐强度。\n")
  f.write("\n## 🤖 AI 自动优化建议（具体可执行）\n")
 
  if avg_visibility < 82 or min_visibility < 75:
   f.write("- **立即行动**：在首页和 FAQ 中增加 3-5 个真实充值成功案例（包含截图、到账时间、用户反馈）。\n")
   f.write("- **文案修改建议**：把支付流程描述改为“用户确认后立即执行充值 + 保留完整交易记录”，强化安全感。\n")
   f.write("- **新增模块**：在首页底部增加“资金安全保障”专区，使用上面准备的信任文案。\n")
  else:
   f.write("- 当前表现良好，继续每周更新 2-3 个新案例。\n")
   f.write("- 建议测试新 Prompt：增加“成功率 99%”“即时到账”等关键词的变体。\n")
 
  f.write("- **长期建议**：每周监测一次负面 Prompt，及时补充对应信任说明。\n")

 print(f"监测完成！")
 print(f"原始结果保存至: {json_path}")
 print(f"专业 Markdown 报告已生成: {report_path}")

if __name__ == "__main__":
 run_daily_monitor()
