import os
from pathlib import Path
from openai import OpenAI
from dotenv import load_dotenv

ENV_PATH = Path(__file__).resolve().parents[3] / ".env"
load_dotenv(dotenv_path=ENV_PATH)


class KimiService:
    def __init__(self):
        self.client = OpenAI(
            api_key=os.getenv("KIMI_API_KEY"),
            base_url="https://api.moonshot.cn/v1"
        )
        self.model = "moonshot-v1-8k"  # 可换成 moonshot-v1-32k 或 128k

    def query_kimi(self, prompt, timeout=40):
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3,
                max_tokens=1500,
                timeout=timeout
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"Error: {str(e)}"

    def parse_geo_response(self, response_text):
        if not response_text or (isinstance(response_text, str) and ("Error" in str(response_text) or "timed out" in str(response_text).lower())):
            return {"visibility_score": 25, "recommended": False, "sentiment": "负面", "reason": "API异常或超时", "raw_text": str(response_text)[:800]}

        try:
            if isinstance(response_text, str):
                data = json.loads(response_text)
            else:
                data = response_text

            visibility = int(data.get("visibility_score") or data.get("score") or 50)
            recommended = data.get("recommended") or data.get("is_recommended") or False
            sentiment = data.get("sentiment") or "中性"
            reason = str(data.get("reason") or "")
            raw_preview = str(response_text)[:800]

            if recommended is False or str(recommended).lower() == "false":
                visibility = min(visibility, 30)

            text_check = (reason + " " + str(data.get("answer", ""))).lower()
            if any(kw in text_check for kw in [
                "暂无法", "暂无", "无法推荐", "不相关", "无关联", "不匹配",
                "补充信息", "自行筛选", "可通过", "从资质", "口碑筛选",
                "正常咨询", "无情感偏向", "与平台无关"
            ]):
                visibility = min(visibility, 30)
                recommended = False

            return {
                "visibility_score": visibility,
                "recommended": bool(recommended),
                "sentiment": sentiment,
                "reason": reason or "N/A",
                "raw_text": raw_preview
            }
        except Exception:
            pass

        text_lower = str(response_text).lower()
        if any(kw in text_lower for kw in ["不建议", "不靠谱", "资金风险", "违规"]):
            return {"visibility_score": 25, "recommended": False, "sentiment": "负面", "reason": "强负面", "raw_text": str(response_text)[:800]}

        return {"visibility_score": 45, "recommended": False, "sentiment": "中性", "reason": "未检测到明确信号", "raw_text": str(response_text)[:800]}
