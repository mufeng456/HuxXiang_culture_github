from app import db
from datetime import datetime


class KnowledgeCategory(db.Model):
    __tablename__ = 'knowledge_categories'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    description = db.Column(db.Text)
    color = db.Column(db.String(20))
    icon = db.Column(db.String(50))
    priority = db.Column(db.Integer, default=0)
    status = db.Column(db.String(20), default='active')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f'<KnowledgeCategory {self.name}>'


class KnowledgeNode(db.Model):
    __tablename__ = 'knowledge_nodes'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, index=True)
    description = db.Column(db.Text)
    category = db.Column(db.String(50), nullable=False, index=True)
    node_type = db.Column(db.String(30), nullable=False)
    level = db.Column(db.Integer, default=2)
    x_position = db.Column(db.Float)
    y_position = db.Column(db.Float)
    color = db.Column(db.String(20))
    icon = db.Column(db.String(50))
    weight = db.Column(db.Integer, default=1)
    status = db.Column(db.String(20), default='active')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f'<KnowledgeNode {self.name}>'


class KnowledgeRelationship(db.Model):
    __tablename__ = 'knowledge_relationships'

    id = db.Column(db.Integer, primary_key=True)
    source_node_id = db.Column(db.Integer, nullable=False, index=True)
    target_node_id = db.Column(db.Integer, nullable=False, index=True)
    relationship_type = db.Column(db.String(50), nullable=False)
    description = db.Column(db.Text)
    strength = db.Column(db.Float, default=1.0)
    direction = db.Column(db.String(10), default='undirected')
    status = db.Column(db.String(20), default='active')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f'<KnowledgeRelationship {self.source_node_id}->{self.target_node_id}>'
