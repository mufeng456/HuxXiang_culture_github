from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from models.knowledge import KnowledgeCategory, KnowledgeNode, KnowledgeRelationship
from models.user import User

knowledge_bp = Blueprint('knowledge', __name__, url_prefix='/api/knowledge')


def _node_to_dict(node):
    return {
        'id': node.id,
        'name': node.name,
        'description': node.description,
        'category': node.category,
        'node_type': node.node_type,
        'level': node.level,
        'x_position': node.x_position,
        'y_position': node.y_position,
        'color': node.color,
        'icon': node.icon,
        'weight': node.weight,
        'status': node.status,
    }


def _category_to_dict(cat):
    return {
        'id': cat.id,
        'name': cat.name,
        'description': cat.description,
        'color': cat.color,
        'icon': cat.icon,
        'priority': cat.priority,
    }


def _relationship_to_dict(rel):
    return {
        'id': rel.id,
        'source_node_id': rel.source_node_id,
        'target_node_id': rel.target_node_id,
        'relationship_type': rel.relationship_type,
        'description': rel.description,
        'strength': rel.strength,
        'direction': rel.direction,
    }


def _require_admin():
    """校验当前用户是否为管理员，返回 (user, error_response)"""
    user_id = get_jwt_identity()
    user = current_app.db.session.get(User, int(user_id))
    if not user or user.role != 'admin':
        return None, (jsonify({'message': '需要管理员权限'}), 403)
    return user, None


@knowledge_bp.route('/graph', methods=['GET'])
def get_graph():
    """获取完整知识图谱（节点+关系），自动构建3层结构"""
    try:
        db = current_app.db.session

        # 1. 查询所有启用的节点和关系
        nodes = db.query(KnowledgeNode).filter(KnowledgeNode.status == 'active').all()
        relationships = db.query(KnowledgeRelationship).filter(KnowledgeRelationship.status == 'active').all()
        categories = db.query(KnowledgeCategory).filter(KnowledgeCategory.status == 'active').all()

        # 2. 找顶层节点（level=1）
        top_node = next((n for n in nodes if n.level == 1), None)
        child_nodes = [n for n in nodes if n.level != 1]

        # 3. 按 category 分组，生成虚拟分类节点（level=2）
        cat_map = {c.name: c for c in categories}
        category_groups = {}
        for n in child_nodes:
            category_groups.setdefault(n.category, []).append(n)

        # 构建结果节点列表
        result_nodes = []
        result_links = []
        virtual_id_counter = 10000  # 虚拟分类节点用大ID避免冲突

        # 顶层节点
        if top_node:
            result_nodes.append({
                'id': top_node.id,
                'name': top_node.name,
                'level': 1,
                'x': top_node.x_position or 0,
                'y': top_node.y_position or 0,
                'color': top_node.color or '#3498db',
                'description': top_node.description,
                'node_type': top_node.node_type,
                'is_virtual': False,
            })

        # 分类节点（虚拟，level=2）
        category_virtual_ids = {}
        for cat_name, cat_nodes in category_groups.items():
            vid = virtual_id_counter
            virtual_id_counter += 1
            category_virtual_ids[cat_name] = vid
            cat_info = cat_map.get(cat_name)
            result_nodes.append({
                'id': vid,
                'name': cat_name,
                'level': 2,
                'category': cat_name,
                'x': 0,  # 前端calculateNodePositions会重新计算
                'y': 0,
                'color': cat_info.color if cat_info else '#95a5a6',
                'description': cat_info.description if cat_info else '',
                'node_type': 'category',
                'is_virtual': True,
            })
            # 顶层 -> 分类
            if top_node:
                result_links.append({'source': top_node.id, 'target': vid, 'level': 2})

        # 实际节点（level=3）
        for n in child_nodes:
            result_nodes.append({
                'id': n.id,
                'name': n.name,
                'level': 3,
                'x': n.x_position or 0,
                'y': n.y_position or 0,
                'color': n.color or '#95a5a6',
                'description': n.description,
                'node_type': n.node_type,
                'category': n.category,
                'is_virtual': False,
            })
            # 分类 -> 节点
            vid = category_virtual_ids.get(n.category)
            if vid:
                result_links.append({'source': vid, 'target': n.id, 'level': 3})

        # 实际关系连线
        for rel in relationships:
            result_links.append({
                'source': rel.source_node_id,
                'target': rel.target_node_id,
                'level': 3,
                'relationship_type': rel.relationship_type,
                'strength': rel.strength,
            })

        return jsonify({
            'success': True,
            'data': {
                'nodes': result_nodes,
                'links': result_links,
                'categories': [_category_to_dict(c) for c in categories],
            }
        })
    except Exception as e:
        return jsonify({'message': '获取知识图谱失败: ' + str(e)}), 500


@knowledge_bp.route('/categories', methods=['GET'])
def get_categories():
    """获取分类列表"""
    try:
        categories = current_app.db.session.query(KnowledgeCategory).filter(
            KnowledgeCategory.status == 'active'
        ).order_by(KnowledgeCategory.priority).all()
        return jsonify({
            'success': True,
            'data': [_category_to_dict(c) for c in categories],
        })
    except Exception as e:
        return jsonify({'message': '获取分类列表失败: ' + str(e)}), 500


@knowledge_bp.route('/nodes', methods=['GET'])
def get_nodes():
    """获取节点列表，支持按分类筛选"""
    try:
        query = current_app.db.session.query(KnowledgeNode).filter(KnowledgeNode.status == 'active')
        category = request.args.get('category')
        if category:
            query = query.filter(KnowledgeNode.category == category)
        nodes = query.order_by(KnowledgeNode.category, KnowledgeNode.id).all()
        return jsonify({
            'success': True,
            'data': [_node_to_dict(n) for n in nodes],
        })
    except Exception as e:
        return jsonify({'message': '获取节点列表失败: ' + str(e)}), 500


@knowledge_bp.route('/nodes/<int:node_id>', methods=['GET'])
def get_node(node_id):
    """获取单个节点详情"""
    try:
        node = current_app.db.session.get(KnowledgeNode, node_id)
        if not node:
            return jsonify({'message': '节点不存在'}), 404
        # 查询关联关系
        rels = current_app.db.session.query(KnowledgeRelationship).filter(
            (KnowledgeRelationship.source_node_id == node_id) |
            (KnowledgeRelationship.target_node_id == node_id)
        ).all()
        return jsonify({
            'success': True,
            'data': _node_to_dict(node),
            'relationships': [_relationship_to_dict(r) for r in rels],
        })
    except Exception as e:
        return jsonify({'message': '获取节点详情失败: ' + str(e)}), 500


@knowledge_bp.route('/nodes', methods=['POST'])
@jwt_required()
def create_node():
    """创建节点（管理员）"""
    _, err = _require_admin()
    if err:
        return err
    try:
        data = request.get_json()
        required = ['name', 'category', 'node_type']
        for f in required:
            if not data.get(f):
                return jsonify({'message': f'{f} 是必需的'}), 400

        node = KnowledgeNode(
            name=data['name'],
            description=data.get('description'),
            category=data['category'],
            node_type=data['node_type'],
            level=data.get('level', 2),
            x_position=data.get('x_position'),
            y_position=data.get('y_position'),
            color=data.get('color'),
            icon=data.get('icon'),
            weight=data.get('weight', 1),
        )
        current_app.db.session.add(node)
        current_app.db.session.commit()
        return jsonify({'success': True, 'message': '节点创建成功', 'data': _node_to_dict(node)}), 201
    except Exception as e:
        current_app.db.session.rollback()
        return jsonify({'message': '创建节点失败: ' + str(e)}), 500


@knowledge_bp.route('/nodes/<int:node_id>', methods=['PUT'])
@jwt_required()
def update_node(node_id):
    """更新节点（管理员）"""
    _, err = _require_admin()
    if err:
        return err
    try:
        node = current_app.db.session.get(KnowledgeNode, node_id)
        if not node:
            return jsonify({'message': '节点不存在'}), 404
        data = request.get_json()
        for field in ['name', 'description', 'category', 'node_type', 'level',
                      'x_position', 'y_position', 'color', 'icon', 'weight', 'status']:
            if field in data:
                setattr(node, field, data[field])
        current_app.db.session.commit()
        return jsonify({'success': True, 'message': '节点更新成功', 'data': _node_to_dict(node)})
    except Exception as e:
        current_app.db.session.rollback()
        return jsonify({'message': '更新节点失败: ' + str(e)}), 500


@knowledge_bp.route('/nodes/<int:node_id>', methods=['DELETE'])
@jwt_required()
def delete_node(node_id):
    """删除节点（管理员），同时删除关联关系"""
    _, err = _require_admin()
    if err:
        return err
    try:
        node = current_app.db.session.get(KnowledgeNode, node_id)
        if not node:
            return jsonify({'message': '节点不存在'}), 404
        # 删除关联关系
        current_app.db.session.query(KnowledgeRelationship).filter(
            (KnowledgeRelationship.source_node_id == node_id) |
            (KnowledgeRelationship.target_node_id == node_id)
        ).delete(synchronize_session=False)
        current_app.db.session.delete(node)
        current_app.db.session.commit()
        return jsonify({'success': True, 'message': '节点删除成功'})
    except Exception as e:
        current_app.db.session.rollback()
        return jsonify({'message': '删除节点失败: ' + str(e)}), 500


@knowledge_bp.route('/relationships', methods=['POST'])
@jwt_required()
def create_relationship():
    """创建关系（管理员）"""
    _, err = _require_admin()
    if err:
        return err
    try:
        data = request.get_json()
        required = ['source_node_id', 'target_node_id', 'relationship_type']
        for f in required:
            if not data.get(f):
                return jsonify({'message': f'{f} 是必需的'}), 400
        rel = KnowledgeRelationship(
            source_node_id=data['source_node_id'],
            target_node_id=data['target_node_id'],
            relationship_type=data['relationship_type'],
            description=data.get('description'),
            strength=data.get('strength', 1.0),
            direction=data.get('direction', 'undirected'),
        )
        current_app.db.session.add(rel)
        current_app.db.session.commit()
        return jsonify({'success': True, 'message': '关系创建成功', 'data': _relationship_to_dict(rel)}), 201
    except Exception as e:
        current_app.db.session.rollback()
        return jsonify({'message': '创建关系失败: ' + str(e)}), 500


@knowledge_bp.route('/relationships/<int:rel_id>', methods=['DELETE'])
@jwt_required()
def delete_relationship(rel_id):
    """删除关系（管理员）"""
    _, err = _require_admin()
    if err:
        return err
    try:
        rel = current_app.db.session.get(KnowledgeRelationship, rel_id)
        if not rel:
            return jsonify({'message': '关系不存在'}), 404
        current_app.db.session.delete(rel)
        current_app.db.session.commit()
        return jsonify({'success': True, 'message': '关系删除成功'})
    except Exception as e:
        current_app.db.session.rollback()
        return jsonify({'message': '删除关系失败: ' + str(e)}), 500
