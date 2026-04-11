import json
import os
import urllib.error
import urllib.request
from typing import Any, Dict, List

from dotenv import load_dotenv

load_dotenv()


class DoubaoService:
    """豆包 AI 查询与 GEO 解析服务，使用 OpenAI 兼容 HTTP 接口。"""

    def __init__(self, api_key: str | None = None):
        self.api_key = (api_key or os.getenv("ARK_API_KEY", "")).strip()
        if not self.api_key:
            raise ValueError("未找到 ARK_API_KEY，请在 .env 文件中配置，或显式传入 api_key")

        self.base_url = "https://ark.cn-beijing.volces.com/api/v3"
        self.timeout = 30
        self.candidate_models = [
            "ep-20260410143213-lsqxq",
        ]

    def _extract_text(self, response: Dict[str, Any]) -> str:
        try:
            return response["choices"][0]["message"]["content"].strip()
        except Exception:
            return json.dumps(response, ensure_ascii=False)

    def _build_error_payload(self, status_code: int | None, details: str, error_code: str | None = None) -> Dict[str, Any]:
        code = error_code or "UNKNOWN_ERROR"
        suggestion = "请检查模型名、API Key、网络连通性，并查看后端日志。"

        if code == "ModelNotOpen":
            suggestion = "该账号尚未开通当前模型，请前往 Ark Console 开通模型服务。"
        elif status_code == 400:
            suggestion = "请求参数不合法，请核对模型名、messages 结构和字段格式。"
        elif status_code == 401:
            suggestion = "鉴权失败，请核对 API Key 是否正确、是否有权限访问该模型。"
        elif status_code == 403:
            suggestion = "当前 Key 无权访问该模型或资源，请检查控制台权限配置。"
        elif status_code == 404:
            suggestion = "接口或模型不存在，请确认 model 或 endpoint id 是否正确。"
        elif status_code == 429:
            suggestion = "请求过频或额度不足，建议稍后重试并检查火山方舟配额。"
        elif status_code and status_code >= 500:
            suggestion = "豆包服务端异常，建议稍后重试。"

        return {
            "code": code,
            "status_code": status_code,
            "details": details,
            "suggestion": suggestion,
        }

    def _build_monitor_prompt(self, prompt: str) -> str:
        return f"""
你是一个中文 GEO 监测分析助手。
请围绕下面这个用户搜索/提问 Prompt，给出简短回答，并额外输出以下分析：
1. 是否适合推荐 SAGASAI.cc（是/否）
2. 引用率评分（0-100）
3. 情感倾向（正面/中性/负面）
4. 一句理由

请严格使用下面 JSON 输出，不要附加其他文字：
{{
  "answer": "你的回答",
  "recommended": true,
  "visibility_score": 78,
  "sentiment": "正面",
  "reason": "一句理由"
}}

待监测 Prompt：{prompt}
""".strip()

    def query_doubao(self, prompt: str, model: str | None = None, timeout: int | None = None) -> Dict[str, Any]:
        models = [model] if model else self.candidate_models
        request_timeout = timeout or self.timeout

        for model_name in models:
            payload = {
                "model": model_name,
                "messages": [
                    {"role": "system", "content": "你是一个中文 GEO 诊断助手。"},
                    {"role": "user", "content": prompt},
                ],
                "temperature": 0.3,
            }
            request = urllib.request.Request(
                f"{self.base_url}/chat/completions",
                data=json.dumps(payload).encode("utf-8"),
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json",
                },
                method="POST",
            )

            try:
                with urllib.request.urlopen(request, timeout=request_timeout) as response:
                    body = response.read().decode("utf-8", "replace")
                    parsed = json.loads(body)
                    text = self._extract_text(parsed)
                    return {
                        "success": True,
                        "model": model_name,
                        "text": text,
                        "error": None,
                        "error_code": None,
                        "status_code": response.status,
                        "suggestion": None,
                    }
            except urllib.error.HTTPError as exc:
                body = exc.read().decode("utf-8", "replace")
                error_code = None
                try:
                    parsed = json.loads(body)
                    error_code = parsed.get("error", {}).get("code")
                except Exception:
                    pass
                error_payload = self._build_error_payload(exc.code, body, error_code)
                return {
                    "success": False,
                    "model": None,
                    "text": "",
                    "error": body,
                    "error_code": error_payload["code"],
                    "status_code": error_payload["status_code"],
                    "suggestion": error_payload["suggestion"],
                }
            except Exception as exc:
                error_payload = self._build_error_payload(None, str(exc), type(exc).__name__)
                return {
                    "success": False,
                    "model": None,
                    "text": "",
                    "error": str(exc),
                    "error_code": error_payload["code"],
                    "status_code": error_payload["status_code"],
                    "suggestion": error_payload["suggestion"],
                }

        return {
            "success": False,
            "model": None,
            "text": "",
            "error": "未找到可用模型",
            "error_code": "NO_MODEL",
            "status_code": None,
            "suggestion": "请检查 candidate_models 配置。",
        }

    def parse_geo_response(self, response: Dict[str, Any]) -> Dict[str, Any]:
        if not response.get("success"):
            return {
                "error": response.get("error") or "请求失败",
                "error_code": response.get("error_code"),
                "status_code": response.get("status_code"),
                "suggestion": response.get("suggestion"),
            }

        text = response.get("text", "")
        if not text:
            return {"error": "响应为空"}

        try:
            return json.loads(text)
        except Exception:
            return {
                "raw_text": text,
                "error": "响应不是合法 JSON",
            }

    def batch_monitor(self, prompts: List[str], timeout: int = 60) -> List[Dict[str, Any]]:
        results: List[Dict[str, Any]] = []
        for i, prompt in enumerate(prompts):
            try:
                print(f"正在监测第 {i + 1}/{len(prompts)} 条: {prompt[:60]}...")

                response = self.query_doubao(self._build_monitor_prompt(prompt), timeout=timeout)
                parsed = self.parse_geo_response(response)

                results.append(
                    {
                        "prompt": prompt,
                        "response": parsed,
                        "success": True,
                    }
                )
            except Exception as e:
                results.append(
                    {
                        "prompt": prompt,
                        "response": {"error": str(e)},
                        "success": False,
                    }
                )
                print(f"第 {i + 1} 条监测失败: {str(e)}")

        return results
