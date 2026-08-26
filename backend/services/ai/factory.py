from .openai_compatible import OpenAICompatibleProvider


def get_provider(config):
    """根据配置返回对应的 AI 服务商实例

    目前所有服务商都使用 OpenAI 兼容格式，
    后续如需支持特殊协议可在此扩展。
    """
    return OpenAICompatibleProvider(config)
