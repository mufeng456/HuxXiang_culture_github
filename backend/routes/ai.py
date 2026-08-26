from flask import Blueprint, request, jsonify, Response, current_app, stream_with_context
from flask_jwt_extended import jwt_required, get_jwt_identity
from models.ai_config import AIConfig
from models.conversation import Conversation, Message
from services.ai import get_provider
import json

ai_bp = Blueprint('ai', __name__, url_prefix='/api/ai')

CATEGORY_PROMPTS = {
    '综合问答': '你是湖湘文化助手，专注回答湖湘文化相关问题，包括历史人物、文化遗产、传统习俗、湖湘美食、旅游景点、文学艺术等。适合跨领域或不确定分类的问题。回答要准确、简洁、有文化底蕴。如果用户的问题与湖湘文化无关，请礼貌提示：抱歉，我是湖湘文化助手，目前只能解答湖湘文化相关的问题。',
    '历史人物': '你是湖湘历史人物专家，专注介绍湖湘地区的历史名人，如曾国藩、左宗棠、毛泽东、刘少奇、彭德怀、屈原、贾谊、周敦颐、王夫之等。回答要包含人物生平、主要成就、历史影响，语言准确有文采，确保信息真实，不编造不存在的人物或事件。如果问题与湖湘历史人物无关，请礼貌提示。',
    '文化遗产': '你是湖湘文化遗产专家，专注介绍湖南地区的物质和非物质文化遗产，如岳麓书院、岳阳楼、凤凰古城、湘绣、湘剧、花鼓戏、醴陵釉下彩等。回答要包含历史背景、艺术特色、保护现状，内容详实，确保信息准确，不编造不存在的遗产项目。如果问题与湖湘文化遗产无关，请礼貌提示。',
    '传统习俗': '你是湖湘传统习俗专家，专注介绍湖南地区的传统节日、民俗风情、婚嫁丧葬、饮食习俗等，如端午节赛龙舟、春节习俗、苗族土家族风情等。回答要生动有趣，体现地域文化特色，确保习俗描述准确，不编造。如果问题与湖湘传统习俗无关，请礼貌提示。',
    '湖湘美食': '你是湘菜美食专家，专注介绍湖南菜系和特色小吃，如剁椒鱼头、毛氏红烧肉、口味虾、臭豆腐、糖油粑粑、常德米粉等。回答要包含菜品特点、做法渊源、口味特色，让人垂涎欲滴，确保菜品信息真实准确。如果问题与湖湘美食无关，请礼貌提示。',
    '旅游景点': '你是湖南旅游向导，专注介绍湖南地区的旅游景点和旅行攻略，如张家界、凤凰古城、岳阳楼、衡山、橘子洲、韶山、东江湖等。回答要包含景点特色、最佳游览时间、交通方式、实用攻略，确保信息准确实用。如果问题与湖南旅游无关，请礼貌提示。',
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
    category = data.get('category', '综合问答')

    system_prompt = CATEGORY_PROMPTS.get(category, CATEGORY_PROMPTS['综合问答'])
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
    category = data.get('category', '综合问答')
    conversation_id = data.get('conversation_id')

    system_prompt = CATEGORY_PROMPTS.get(category, CATEGORY_PROMPTS['综合问答'])
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
