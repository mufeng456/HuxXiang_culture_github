from flask import Blueprint, request, jsonify, Response, current_app, stream_with_context
from flask_jwt_extended import jwt_required, get_jwt_identity
from models.ai_config import AIConfig
from models.conversation import Conversation, Message
from services.ai import get_provider
import json

ai_bp = Blueprint('ai', __name__, url_prefix='/api/ai')

CATEGORY_PROMPTS = {
    '文化问答': '你是一位湖湘文化专家，请用通俗易懂的语言回答关于湖湘文化的问题。',
    '历史人物': '你是一位研究湖南历史人物的学者，请详细介绍湖南历史上的著名人物及其事迹。',
    '文化遗产': '你是一位文化遗产保护专家，请介绍湖南的非物质文化遗产和物质文化遗产。',
    '传统习俗': '你是一位民俗学专家，请介绍湖南地区的传统习俗、节日和礼仪。',
    '湖湘美食': '你是一位湘菜美食家，请介绍湖南的特色美食、饮食文化和烹饪方法。',
    '旅游景点': '你是一位湖南旅游向导，请推荐湖南的旅游景点、路线和旅行建议。',
}


def get_config():
    config = current_app.db.session.query(AIConfig).first()
    if not config or not config.api_key:
        return None
    return config


@ai_bp.route('/chat', methods=['POST'])
def chat():
    config = get_config()
    if not config:
        return jsonify({'error': 'AI 服务未配置，请联系管理员'}), 503

    data = request.get_json()
    messages = data.get('messages', [])
    category = data.get('category', '文化问答')

    system_prompt = CATEGORY_PROMPTS.get(category, CATEGORY_PROMPTS['文化问答'])
    full_messages = [{'role': 'system', 'content': system_prompt}] + messages

    try:
        provider = get_provider(config)
        reply = provider.chat(full_messages)
        return jsonify({'reply': reply})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@ai_bp.route('/chat/stream', methods=['POST'])
def chat_stream():
    config = get_config()
    if not config:
        def error_gen():
            yield f'data: {json.dumps({"error": "AI 服务未配置"})}\n\n'
        return Response(error_gen(), mimetype='text/event-stream')

    data = request.get_json()
    messages = data.get('messages', [])
    category = data.get('category', '文化问答')
    conversation_id = data.get('conversation_id')

    system_prompt = CATEGORY_PROMPTS.get(category, CATEGORY_PROMPTS['文化问答'])
    full_messages = [{'role': 'system', 'content': system_prompt}] + messages

    user_id = None
    try:
        user_id = int(get_jwt_identity())
    except Exception:
        pass

    def generate():
        conv = None
        if user_id:
            if conversation_id:
                conv = current_app.db.session.get(Conversation, conversation_id)
            if not conv:
                conv = Conversation(user_id=user_id, title=messages[0]['content'][:30] if messages else '新对话', category=category)
                current_app.db.session.add(conv)
                current_app.db.session.flush()
                # 保存用户消息
                for msg in messages:
                    current_app.db.session.add(Message(conversation_id=conv.id, role=msg['role'], content=msg['content']))
                current_app.db.session.commit()

        try:
            provider = get_provider(config)
            full_reply = ''
            for chunk in provider.chat_stream(full_messages):
                full_reply += chunk
                yield f'data: {json.dumps({"content": chunk, "conversation_id": conv.id if conv else None})}\n\n'

            # 保存 AI 回复
            if conv and full_reply:
                current_app.db.session.add(Message(conversation_id=conv.id, role='assistant', content=full_reply))
                conv.title = messages[0]['content'][:30] if messages else conv.title
                current_app.db.session.commit()

            yield f'data: {json.dumps({"done": True, "conversation_id": conv.id if conv else None})}\n\n'
        except Exception as e:
            yield f'data: {json.dumps({"error": str(e)})}\n\n'

    return Response(stream_with_context(generate()), mimetype='text/event-stream')


@ai_bp.route('/conversations', methods=['GET'])
@jwt_required()
def list_conversations():
    user_id = int(get_jwt_identity())
    convs = current_app.db.session.query(Conversation).filter_by(user_id=user_id).order_by(Conversation.updated_at.desc()).all()
    return jsonify({'conversations': [c.to_dict() for c in convs]})


@ai_bp.route('/conversations/<int:conv_id>', methods=['GET'])
@jwt_required()
def get_conversation(conv_id):
    user_id = int(get_jwt_identity())
    conv = current_app.db.session.get(Conversation, conv_id)
    if not conv or conv.user_id != user_id:
        return jsonify({'error': '对话不存在'}), 404
    msgs = current_app.db.session.query(Message).filter_by(conversation_id=conv_id).order_by(Message.created_at).all()
    return jsonify({'conversation': conv.to_dict(), 'messages': [m.to_dict() for m in msgs]})


@ai_bp.route('/conversations/<int:conv_id>', methods=['DELETE'])
@jwt_required()
def delete_conversation(conv_id):
    user_id = int(get_jwt_identity())
    conv = current_app.db.session.get(Conversation, conv_id)
    if not conv or conv.user_id != user_id:
        return jsonify({'error': '对话不存在'}), 404
    current_app.db.session.delete(conv)
    current_app.db.session.commit()
    return jsonify({'message': '对话已删除'})
