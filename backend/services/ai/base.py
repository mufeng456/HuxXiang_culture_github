from abc import ABC, abstractmethod
from typing import List, Dict


class BaseAIProvider(ABC):
    """AI 服务商抽象基类，所有服务商必须实现 chat 方法"""

    name: str = "base"

    @abstractmethod
    def chat(self, messages: List[Dict[str, str]], system_prompt: str = "") -> str:
        """
        统一对话接口

        Args:
            messages: 对话历史，格式 [{"role": "user"/"assistant", "content": "..."}]
            system_prompt: 系统提示词，用于设定 AI 角色和行为

        Returns:
            AI 回复的文本内容
        """
        raise NotImplementedError

    def _build_full_messages(self, messages: List[Dict[str, str]], system_prompt: str) -> List[Dict[str, str]]:
        """构建包含系统提示词的完整消息列表"""
        full = []
        if system_prompt:
            full.append({"role": "system", "content": system_prompt})
        full.extend(messages)
        return full
