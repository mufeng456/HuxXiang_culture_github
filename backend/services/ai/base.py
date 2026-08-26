from abc import ABC, abstractmethod


class BaseAIProvider(ABC):
    """AI 服务商基类"""

    def __init__(self, config):
        self.config = config
        self.api_key = config.api_key
        self.api_base_url = config.api_base_url.rstrip('/')
        self.model = config.model

    @abstractmethod
    def chat(self, messages):
        """同步对话"""
        pass

    @abstractmethod
    def chat_stream(self, messages):
        """流式对话，返回生成器"""
        pass
