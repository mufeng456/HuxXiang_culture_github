import os
import json
import urllib.request
import urllib.error
from .base import BaseAIProvider


def _post_json(url, headers, payload, timeout=60):
    data = json.dumps(payload).encode('utf-8')
    req = urllib.request.Request(url, data=data, headers=headers, method='POST')
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return json.loads(resp.read().decode('utf-8'))
    except urllib.error.HTTPError as e:
        body = e.read().decode('utf-8', errors='replace')
        raise Exception(f"HTTP {e.code}: {body}")


class OpenAICompatibleProvider(BaseAIProvider):
    """通用 OpenAI 兼容格式 Provider，支持豆包/通义千问/文心一言/OpenAI 等所有兼容厂商"""

    name = "openai-compatible"

    def __init__(self, api_key="", model="", base_url=""):
        self.api_key = api_key
        self.model = model
        self.base_url = base_url.rstrip('/') if base_url else ""

    def chat(self, messages, system_prompt=""):
        if not self.api_key:
            raise ValueError("未配置 API Key，请在管理后台 AI 配置中填写")
        if not self.base_url:
            raise ValueError("未配置接口地址")
        if not self.model:
            raise ValueError("未配置模型名称")

        full_messages = self._build_full_messages(messages, system_prompt)

        data = _post_json(
            f"{self.base_url}/chat/completions",
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            },
            payload={
                "model": self.model,
                "messages": full_messages,
                "temperature": 0.7,
            },
        )
        return data["choices"][0]["message"]["content"]
