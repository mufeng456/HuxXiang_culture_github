from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from models.ai_config import AIConfig
from services.ai import get_provider

admin_ai_config_bp = Blueprint('admin_ai_config', __name__, url_prefix='/api/admin/ai-config')


def get_config():
    config = current_app.db.session.query(AIConfig).first()
    if not config:
        config = AIConfig()
        current_app.db.session.add(config)
        current_app.db.session.commit()
    return config


@admin_ai_config_bp.route('/', methods=['GET'])
@jwt_required()
def get_ai_config():
    config = get_config()
    return jsonify(config.to_dict())


@admin_ai_config_bp.route('/', methods=['PUT'])
@jwt_required()
def update_ai_config():
    data = request.get_json()
    config = get_config()

    if 'provider_name' in data:
        config.provider_name = data['provider_name']
    if 'api_base_url' in data:
        config.api_base_url = data['api_base_url']
    if 'api_key' in data and data['api_key']:
        config.api_key = data['api_key']
    if 'model' in data:
        config.model = data['model']

    current_app.db.session.commit()
    return jsonify({'message': '配置已保存', 'config': config.to_dict()})


@admin_ai_config_bp.route('/', methods=['DELETE'])
@jwt_required()
def clear_ai_config():
    config = get_config()
    config.provider_name = 'OpenAI'
    config.api_base_url = 'https://api.openai.com/v1'
    config.api_key = ''
    config.model = 'gpt-3.5-turbo'
    current_app.db.session.commit()
    return jsonify({'message': '配置已清除', 'config': config.to_dict()})


@admin_ai_config_bp.route('/test', methods=['POST'])
@jwt_required()
def test_ai_connection():
    config = get_config()
    if not config.api_key:
        return jsonify({'error': 'API Key 未配置'}), 400

    try:
        provider = get_provider(config)
        reply = provider.chat([{'role': 'user', 'content': '你好，请回复"连接成功"'}])
        return jsonify({'message': '连接成功', 'reply': reply})
    except Exception as e:
        return jsonify({'error': str(e)}), 500
