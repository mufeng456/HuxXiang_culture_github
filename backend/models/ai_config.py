from app import db
from datetime import datetime


class AIConfig(db.Model):
    __tablename__ = 'ai_config'

    id = db.Column(db.Integer, primary_key=True)
    provider_name = db.Column(db.String(100), nullable=False, default='OpenAI')
    api_base_url = db.Column(db.String(500), nullable=False, default='https://api.openai.com/v1')
    api_key = db.Column(db.String(500), nullable=False, default='')
    model = db.Column(db.String(100), nullable=False, default='gpt-3.5-turbo')
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'provider_name': self.provider_name,
            'api_base_url': self.api_base_url,
            'api_key': self.api_key[-4:] if self.api_key else '',
            'model': self.model,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
