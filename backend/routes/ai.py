import json
import time
from flask import Blueprint, request, jsonify, Response, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity

from services.ai import get_provider
from models.user import User
from models.conversation import Conversation, Message

ai_bp = Blueprint('ai', __name__, url_prefix='/api/ai')

# 各分类的系统提示词
CATEGORY_PROMPTS = {
    "文化问答": (
        "你是湖湘文化助手，专注回答湖湘文化相关问题，"
        "包括历史人物、文化遗产、传统习俗、湖湘美食、旅游景点、文学艺术等。"
        "回答要准确、简洁、有文化底蕴。"
        "如果用户的问题与湖湘文化无关，请礼貌提示：抱歉，我是湖湘文化助手，目前只能解答湖湘文化相关的问题。"
    ),
    "历史人物": (
        "你是湖湘历史人物专家，专注介绍湖湘地区的历史名人，"
        "如曾国藩、左宗棠、毛泽东、刘少奇、彭德怀、屈原、贾谊、周敦颐、王夫之等。"
        "回答要包含人物生平、主要成就、历史影响，语言准确有文采。"
        "如果问题与湖湘历史人物无关，请礼貌提示。"
    ),
    "文化遗产": (
        "你是湖湘文化遗产专家，专注介绍湖南地区的物质和非物质文化遗产，"
        "如岳麓书院、岳阳楼、凤凰古城、湘绣、湘剧、花鼓戏、醴陵釉下彩等。"
        "回答要包含历史背景、艺术特色、保护现状，内容详实。"
        "如果问题与湖湘文化遗产无关，请礼貌提示。"
    ),
    "传统习俗": (
        "你是湖湘传统习俗专家，专注介绍湖南地区的传统节日、民俗风情、婚嫁丧葬、饮食习俗等，"
        "如端午节赛龙舟、春节习俗、苗族土家族风情等。"
        "回答要生动有趣，体现地域文化特色。"
        "如果问题与湖湘传统习俗无关，请礼貌提示。"
    ),
    "湖湘美食": (
        "你是湘菜美食专家，专注介绍湖南菜系和特色小吃，"
        "如剁椒鱼头、毛氏红烧肉、口味虾、臭豆腐、糖油粑粑、常德米粉等。"
        "回答要包含菜品特点、做法渊源、口味特色，让人垂涎欲滴。"
        "如果问题与湖湘美食无关，请礼貌提示。"
    ),
    "旅游景点": (
        "你是湖南旅游向导，专注介绍湖南地区的旅游景点和旅行攻略，"
        "如张家界、凤凰古城、岳阳楼、衡山、橘子洲、韶山、东江湖等。"
        "回答要包含景点特色、最佳游览时间、交通方式、实用攻略。"
        "如果问题与湖南旅游无关，请礼貌提示。"
    ),
}

DEFAULT_PROMPT = CATEGORY_PROMPTS["文化问答"]


def _get_system_prompt(category):
    """根据分类获取系统提示词"""
    return CATEGORY_PROMPTS.get(category, DEFAULT_PROMPT)


def _get_current_user():
    """从 JWT 获取当前用户，未登录返回 None"""
    try:
        user_id = get_jwt_identity()
        if user_id:
            return current_app.db.session.get(User, int(user_id))
    except Exception:
        pass
    return None


@ai_bp.route('/chat', methods=['POST'])
@jwt_required(optional=True)
def chat():
    """AI 对话接口（非流式，保存到数据库）

    Request Body:
        messages: [{"role": "user"/"assistant", "content": "..."}]
        category: 可选，分类
        conversation_id: 可选，已有对话ID

    Response:
        {"reply": "...", "provider": "...", "conversation_id": 1}
    """
    try:
        data = request.get_json()
        if not data or 'messages' not in data:
            return jsonify({'message': '缺少 messages 参数'}), 400

        messages = data['messages']
        if not isinstance(messages, list) or len(messages) == 0:
            return jsonify({'message': 'messages 不能为空'}), 400

        category = data.get('category', '文化问答')
        system_prompt = _get_system_prompt(category)

        provider = get_provider()
        reply = provider.chat(messages, system_prompt=system_prompt)

        # 保存对话到数据库（登录用户）
        conversation_id = data.get('conversation_id')
        user = _get_current_user()
        if user:
            db = current_app.db.session
            if not conversation_id:
                # 创建新对话，标题取用户第一条消息
                first_user_msg = next((m['content'] for m in messages if m['role'] == 'user'), '新对话')
                title = first_user_msg[:30] if len(first_user_msg) > 30 else first_user_msg
                conv = Conversation(user_id=user.id, category=category, title=title)
                db.add(conv)
                db.flush()
                conversation_id = conv.id
                # 保存历史消息
                for m in messages[:-1]:
                    db.add(Message(conversation_id=conv.id, role=m['role'], content=m['content']))
            else:
                conv = db.get(Conversation, conversation_id)
                if conv and conv.user_id == user.id:
                    conv.updated_at = db.func.now()
            # 保存当前用户消息和 AI 回复
            last_user_msg = messages[-1]['content'] if messages[-1]['role'] == 'user' else ''
            if last_user_msg:
                db.add(Message(conversation_id=conversation_id, role='user', content=last_user_msg))
            db.add(Message(conversation_id=conversation_id, role='assistant', content=reply))
            db.commit()

        return jsonify({
            'reply': reply,
            'provider': provider.name,
            'conversation_id': conversation_id,
        })
    except ValueError as e:
        return jsonify({'message': str(e)}), 400
    except Exception as e:
        return jsonify({'message': f'AI 服务异常: {str(e)}'}), 500


@ai_bp.route('/chat/stream', methods=['POST'])
@jwt_required(optional=True)
def chat_stream():
    """AI 对话流式输出接口（SSE）"""
    data = request.get_json()
    if not data or 'messages' not in data:
        return jsonify({'message': '缺少 messages 参数'}), 400

    messages = data['messages']
    category = data.get('category', '文化问答')
    system_prompt = _get_system_prompt(category)
    conversation_id = data.get('conversation_id')

    # 在请求上下文中提前获取 provider 和 user（generator 内 app context 可能不可用）
    try:
        provider = get_provider()
    except Exception as e:
        return jsonify({'message': str(e)}), 400

    user = _get_current_user()
    db_session = current_app.db.session

    def generate():
        try:
            # 非流式模式下先获取完整回复，再逐字输出（模拟流式）
            reply = provider.chat(messages, system_prompt=system_prompt)
            conv_id = conversation_id

            # 保存到数据库
            if user:
                if not conv_id:
                    first_user_msg = next((m['content'] for m in messages if m['role'] == 'user'), '新对话')
                    title = first_user_msg[:30]
                    conv = Conversation(user_id=user.id, category=category, title=title)
                    db_session.add(conv)
                    db_session.flush()
                    conv_id = conv.id
                    for m in messages[:-1]:
                        db_session.add(Message(conversation_id=conv.id, role=m['role'], content=m['content']))
                last_user_msg = messages[-1]['content'] if messages[-1]['role'] == 'user' else ''
                if last_user_msg:
                    db_session.add(Message(conversation_id=conv_id, role='user', content=last_user_msg))
                db_session.add(Message(conversation_id=conv_id, role='assistant', content=reply))
                db_session.commit()

            # 逐字输出
            for char in reply:
                yield f"data: {json.dumps({'content': char, 'conversation_id': conv_id}, ensure_ascii=False)}\n\n"
                time.sleep(0.02)
            yield f"data: {json.dumps({'done': True}, ensure_ascii=False)}\n\n"
        except Exception as e:
            yield f"data: {json.dumps({'error': str(e)}, ensure_ascii=False)}\n\n"

    return Response(generate(), mimetype='text/event-stream', headers={
        'Cache-Control': 'no-cache',
        'X-Accel-Buffering': 'no',
    })


@ai_bp.route('/conversations', methods=['GET'])
@jwt_required()
def list_conversations():
    """获取当前用户的对话列表"""
    user = _get_current_user()
    if not user:
        return jsonify({'message': '请先登录'}), 401

    try:
        db = current_app.db.session
        convs = db.query(Conversation).filter_by(user_id=user.id).order_by(Conversation.updated_at.desc()).all()
        return jsonify({'conversations': [c.to_dict() for c in convs]})
    except Exception as e:
        return jsonify({'message': f'获取对话列表失败: {str(e)}'}), 500


@ai_bp.route('/conversations/<int:conv_id>', methods=['GET'])
@jwt_required()
def get_conversation(conv_id):
    """获取单个对话及其消息"""
    user = _get_current_user()
    if not user:
        return jsonify({'message': '请先登录'}), 401

    try:
        db = current_app.db.session
        conv = db.get(Conversation, conv_id)
        if not conv or conv.user_id != user.id:
            return jsonify({'message': '对话不存在'}), 404

        msgs = db.query(Message).filter_by(conversation_id=conv_id).order_by(Message.created_at.asc()).all()
        return jsonify({
            'conversation': conv.to_dict(),
            'messages': [m.to_dict() for m in msgs],
        })
    except Exception as e:
        return jsonify({'message': f'获取对话失败: {str(e)}'}), 500


@ai_bp.route('/conversations/<int:conv_id>', methods=['DELETE'])
@jwt_required()
def delete_conversation(conv_id):
    """删除对话"""
    user = _get_current_user()
    if not user:
        return jsonify({'message': '请先登录'}), 401

    try:
        db = current_app.db.session
        conv = db.get(Conversation, conv_id)
        if not conv or conv.user_id != user.id:
            return jsonify({'message': '对话不存在'}), 404

        db.delete(conv)
        db.commit()
        return jsonify({'message': '对话已删除'})
    except Exception as e:
        db.rollback()
        return jsonify({'message': f'删除失败: {str(e)}'}), 500


@ai_bp.route('/providers', methods=['GET'])
def list_providers():
    """获取支持的 AI 服务商预设"""
    from services.ai import list_providers
    return jsonify({'providers': list_providers()})
