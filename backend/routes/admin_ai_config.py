from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity

from models.user import User
from models.ai_config import AIConfig

admin_ai_config_bp = Blueprint('admin_ai_config', __name__, url_prefix='/api/admin/ai-config')


def _require_admin():
    user_id = get_jwt_identity()
    user = current_app.db.session.get(User, int(user_id))
    if not user or user.role != 'admin':
        return None, (jsonify({'message': '需要管理员权限'}), 403)
    return user, None


def _is_masked(value):
    return isinstance(value, str) and value.startswith('****')


@admin_ai_config_bp.route('/', methods=['GET'])
@jwt_required()
def get_config():
    """获取 AI 配置（API key 脱敏）"""
    _, error = _require_admin()
    if error:
        return error

    try:
        config = AIConfig.get_config()
        return jsonify(config.to_dict(mask_key=True))
    except Exception as e:
        return jsonify({'message': f'获取配置失败: {str(e)}'}), 500


@admin_ai_config_bp.route('/', methods=['PUT'])
@jwt_required()
def update_config():
    """更新 AI 配置，脱敏的 key 不更新"""
    _, error = _require_admin()
    if error:
        return error

    try:
        db = current_app.db.session
        config = AIConfig.get_config()
        data = request.get_json()

        if 'provider_name' in data:
            config.provider_name = data['provider_name']

        if 'api_base_url' in data:
            config.api_base_url = data['api_base_url']

        if 'model' in data:
            config.model = data['model']

        # 只有不是脱敏值时才更新 key
        if 'api_key' in data and not _is_masked(data['api_key']):
            config.api_key = data['api_key']

        db.commit()
        return jsonify({'message': '配置更新成功', 'config': config.to_dict(mask_key=True)})
    except Exception as e:
        db.rollback()
        return jsonify({'message': f'更新配置失败: {str(e)}'}), 500


@admin_ai_config_bp.route('/', methods=['DELETE'])
@jwt_required()
def clear_config():
    """清除 AI 配置（重置为默认，清空 API Key）"""
    _, error = _require_admin()
    if error:
        return error

    try:
        db = current_app.db.session
        config = AIConfig.get_config()
        config.provider_name = '字节豆包'
        config.api_base_url = 'https://ark.cn-beijing.volces.com/api/v3'
        config.api_key = ''
        config.model = 'doubao-pro-32k'
        db.commit()
        return jsonify({'message': '配置已清除', 'config': config.to_dict(mask_key=True)})
    except Exception as e:
        db.rollback()
        return jsonify({'message': f'清除配置失败: {str(e)}'}), 500


@admin_ai_config_bp.route('/test', methods=['POST'])
@jwt_required()
def test_connection():
    """测试当前 AI 配置是否能正常连接"""
    _, error = _require_admin()
    if error:
        return error

    try:
        from services.ai import get_provider
        provider = get_provider()

        if not provider.api_key:
            return jsonify({'success': False, 'message': '未配置 API Key'}), 400

        # 发一条简单的测试消息
        reply = provider.chat(
            messages=[{"role": "user", "content": "请回复“连接成功”四个字"}],
            system_prompt="你是一个测试助手，只需要回复指定内容。"
        )
        return jsonify({'success': True, 'message': '连接成功', 'reply': reply[:100]})
    except ValueError as e:
        return jsonify({'success': False, 'message': str(e)}), 400
    except Exception as e:
        return jsonify({'success': False, 'message': f'连接失败: {str(e)}'}), 500
