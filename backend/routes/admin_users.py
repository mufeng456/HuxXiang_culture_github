from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity

from models.user import User

admin_users_bp = Blueprint('admin_users', __name__, url_prefix='/api/admin/users')


def _user_to_dict(user):
    return {
        'id': user.id,
        'username': user.username,
        'email': user.email,
        'avatar': user.avatar,
        'bio': user.bio,
        'role': user.role,
        'is_active': user.is_active,
        'created_at': user.created_at.isoformat() if user.created_at else None,
        'updated_at': user.updated_at.isoformat() if user.updated_at else None,
    }


def _require_admin():
    """校验当前用户是否为管理员，返回 (user, error_response)"""
    user_id = get_jwt_identity()
    user = current_app.db.session.get(User, int(user_id))
    if not user or user.role != 'admin':
        return None, (jsonify({'message': '需要管理员权限'}), 403)
    return user, None


@admin_users_bp.route('/', methods=['GET'])
@jwt_required()
def list_users():
    """获取用户列表（支持分页、搜索、角色筛选）"""
    admin, error = _require_admin()
    if error:
        return error

    try:
        db = current_app.db.session
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        search = request.args.get('search', '').strip()
        role = request.args.get('role', '').strip()

        query = db.query(User)

        if search:
            query = query.filter(
                (User.username.ilike(f'%{search}%')) |
                (User.email.ilike(f'%{search}%'))
            )

        if role:
            query = query.filter(User.role == role)

        query = query.order_by(User.created_at.desc())
        pagination = query.paginate(page=page, per_page=per_page, error_out=False)

        return jsonify({
            'users': [_user_to_dict(u) for u in pagination.items],
            'total': pagination.total,
            'page': page,
            'per_page': per_page,
            'total_pages': pagination.pages,
        })
    except Exception as e:
        return jsonify({'message': f'获取用户列表失败: {str(e)}'}), 500


@admin_users_bp.route('/<int:user_id>', methods=['GET'])
@jwt_required()
def get_user(user_id):
    """获取用户详情"""
    admin, error = _require_admin()
    if error:
        return error

    try:
        db = current_app.db.session
        user = db.get(User, user_id)
        if not user:
            return jsonify({'message': '用户不存在'}), 404
        return jsonify(_user_to_dict(user))
    except Exception as e:
        return jsonify({'message': f'获取用户失败: {str(e)}'}), 500


@admin_users_bp.route('/', methods=['POST'])
@jwt_required()
def create_user():
    """管理员创建用户"""
    admin, error = _require_admin()
    if error:
        return error

    try:
        db = current_app.db.session
        data = request.get_json()

        username = (data.get('username') or '').strip()
        email = (data.get('email') or '').strip()
        password = data.get('password') or ''
        role = data.get('role', 'user')
        is_active = data.get('is_active', True)

        if not username or len(username) < 3:
            return jsonify({'message': '用户名至少3个字符'}), 400
        if not email or '@' not in email:
            return jsonify({'message': '邮箱格式不正确'}), 400
        if not password or len(password) < 6:
            return jsonify({'message': '密码至少6个字符'}), 400
        if role not in ('user', 'admin'):
            return jsonify({'message': '角色只能是 user 或 admin'}), 400

        if db.query(User).filter_by(username=username).first():
            return jsonify({'message': '用户名已存在'}), 400
        if db.query(User).filter_by(email=email).first():
            return jsonify({'message': '邮箱已存在'}), 400

        user = User(
            username=username,
            email=email,
            role=role,
            is_active=is_active,
        )
        user.set_password(password)
        db.add(user)
        db.commit()

        return jsonify({'message': '用户创建成功', 'user': _user_to_dict(user)}), 201
    except Exception as e:
        db.rollback()
        return jsonify({'message': f'创建用户失败: {str(e)}'}), 500


@admin_users_bp.route('/<int:user_id>', methods=['PUT'])
@jwt_required()
def update_user(user_id):
    """管理员更新用户信息"""
    admin, error = _require_admin()
    if error:
        return error

    try:
        db = current_app.db.session
        user = db.get(User, user_id)
        if not user:
            return jsonify({'message': '用户不存在'}), 404

        data = request.get_json()

        if 'username' in data:
            new_username = (data['username'] or '').strip()
            if len(new_username) < 3:
                return jsonify({'message': '用户名至少3个字符'}), 400
            existing = db.query(User).filter_by(username=new_username).first()
            if existing and existing.id != user_id:
                return jsonify({'message': '用户名已存在'}), 400
            user.username = new_username

        if 'email' in data:
            new_email = (data['email'] or '').strip()
            if '@' not in new_email:
                return jsonify({'message': '邮箱格式不正确'}), 400
            existing = db.query(User).filter_by(email=new_email).first()
            if existing and existing.id != user_id:
                return jsonify({'message': '邮箱已存在'}), 400
            user.email = new_email

        if 'role' in data:
            if data['role'] not in ('user', 'admin'):
                return jsonify({'message': '角色只能是 user 或 admin'}), 400
            # 防止管理员把自己降级
            if user.id == admin.id and data['role'] != 'admin':
                return jsonify({'message': '不能修改自己的管理员角色'}), 400
            user.role = data['role']

        if 'is_active' in data:
            # 防止管理员禁用自己
            if user.id == admin.id and not data['is_active']:
                return jsonify({'message': '不能禁用自己的账号'}), 400
            user.is_active = data['is_active']

        if 'bio' in data:
            user.bio = data['bio']

        if 'password' in data and data['password']:
            if len(data['password']) < 6:
                return jsonify({'message': '密码至少6个字符'}), 400
            user.set_password(data['password'])

        db.commit()
        return jsonify({'message': '用户更新成功', 'user': _user_to_dict(user)})
    except Exception as e:
        db.rollback()
        return jsonify({'message': f'更新用户失败: {str(e)}'}), 500


@admin_users_bp.route('/<int:user_id>', methods=['DELETE'])
@jwt_required()
def delete_user(user_id):
    """管理员删除用户"""
    admin, error = _require_admin()
    if error:
        return error

    try:
        db = current_app.db.session
        user = db.get(User, user_id)
        if not user:
            return jsonify({'message': '用户不存在'}), 404

        if user.id == admin.id:
            return jsonify({'message': '不能删除自己的账号'}), 400

        db.delete(user)
        db.commit()
        return jsonify({'message': '用户删除成功'})
    except Exception as e:
        db.rollback()
        return jsonify({'message': f'删除用户失败: {str(e)}'}), 500
