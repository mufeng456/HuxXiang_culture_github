from datetime import datetime

from flask import current_app
from app import db


class AIConfig(db.Model):
    """AI 服务商配置，通用 OpenAI 兼容格式，支持所有兼容厂商"""
    __tablename__ = "ai_config"

    id = db.Column(db.Integer, primary_key=True)
    provider_name = db.Column(db.String(50), default="字节豆包")
    api_base_url = db.Column(db.String(512), default="https://ark.cn-beijing.volces.com/api/v3")
    api_key = db.Column(db.String(512), default="")
    model = db.Column(db.String(128), default="doubao-pro-32k")
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self, mask_key=True):
        def mask(key):
            if not key:
                return ""
            if mask_key and len(key) > 4:
                return "****" + key[-4:]
            return key

        return {
            'provider_name': self.provider_name,
            'api_base_url': self.api_base_url,
            'api_key': mask(self.api_key),
            'model': self.model,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }

    @classmethod
    def get_config(cls):
        """获取单条配置，不存在则创建默认配置"""
        session = current_app.db.session
        config = session.query(cls).first()
        if not config:
            config = cls()
            session.add(config)
            session.commit()
        return config
