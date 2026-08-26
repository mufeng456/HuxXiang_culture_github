import os
from .base import BaseAIProvider
from .openai_compatible import OpenAICompatibleProvider


def get_provider() -> BaseAIProvider:
    """
    获取 AI 服务商实例
    优先从数据库读取配置，数据库未配置时回退到环境变量
    """
    # 尝试从数据库读取配置
    try:
        from models.ai_config import AIConfig
        config = AIConfig.get_config()
        if config and config.api_key:
            return OpenAICompatibleProvider(
                api_key=config.api_key,
                model=config.model,
                base_url=config.api_base_url,
            )
    except Exception:
        pass

    # 回退到环境变量
    return OpenAICompatibleProvider(
        api_key=os.getenv("OPENAI_API_KEY", ""),
        model=os.getenv("OPENAI_MODEL", "gpt-3.5-turbo"),
        base_url=os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1"),
    )


def list_providers() -> list:
    """返回常用服务商预设，用于前端快速填充"""
    return [
        {
            'name': '字节豆包',
            'base_url': 'https://ark.cn-beijing.volces.com/api/v3',
            'model': 'doubao-pro-32k',
        },
        {
            'name': '阿里通义千问',
            'base_url': 'https://dashscope.aliyuncs.com/compatible-mode/v1',
            'model': 'qwen-turbo',
        },
        {
            'name': '百度文心一言',
            'base_url': 'https://qianfan.baidubce.com/v2',
            'model': 'ernie-3.5-turbo',
        },
        {
            'name': 'OpenAI',
            'base_url': 'https://api.openai.com/v1',
            'model': 'gpt-3.5-turbo',
        },
        {
            'name': '自定义',
            'base_url': '',
            'model': '',
        },
    ]
