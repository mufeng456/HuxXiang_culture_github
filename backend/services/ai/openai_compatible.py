import requests
import json
from .base import BaseAIProvider


class OpenAICompatibleProvider(BaseAIProvider):
    """OpenAI 兼容格式的 AI 服务商

    支持：OpenAI、字节豆包、阿里通义千问、百度文心一言等
    所有兼容 /v1/chat/completions 接口的服务商。
    """

    def chat(self, messages):
        url = f"{self.api_base_url}/chat/completions"
        headers = {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json'
        }
        payload = {
            'model': self.model,
            'messages': messages,
            'stream': False
        }
        resp = requests.post(url, headers=headers, json=payload, timeout=60)
        resp.raise_for_status()
        data = resp.json()
        return data['choices'][0]['message']['content']

    def chat_stream(self, messages):
        url = f"{self.api_base_url}/chat/completions"
        headers = {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json'
        }
        payload = {
            'model': self.model,
            'messages': messages,
            'stream': True
        }

        resp = requests.post(url, headers=headers, json=payload, stream=True, timeout=60)
        resp.raise_for_status()

        for line in resp.iter_lines(decode_unicode=True):
            if line and line.startswith('data: '):
                data_str = line[6:]
                if data_str == '[DONE]':
                    break
                try:
                    data = json.loads(data_str)
                    delta = data['choices'][0].get('delta', {})
                    content = delta.get('content', '')
                    if content:
                        yield content
                except (json.JSONDecodeError, KeyError, IndexError):
                    continue
