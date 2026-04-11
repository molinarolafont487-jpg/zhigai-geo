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
        # 后续可以让 Grok 帮我们完善解析逻辑
        return {"raw_response": response_text}
