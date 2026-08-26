from flask import Flask
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from flask_sqlalchemy import SQLAlchemy
from werkzeug.exceptions import HTTPException

from config import Config


db = SQLAlchemy()
jwt = JWTManager()


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    app.db = db

    CORS(app)
    jwt.init_app(app)

    from routes.auth import auth_bp
    from routes.cultural_resources import cultural_resources_bp
    from routes.knowledge import knowledge_bp
    from routes.admin_users import admin_users_bp
    from routes.ai import ai_bp
    from routes.admin_ai_config import admin_ai_config_bp
    from routes.main import main_bp

    app.register_blueprint(main_bp)
    app.register_blueprint(cultural_resources_bp)
    app.register_blueprint(knowledge_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(admin_users_bp)
    app.register_blueprint(ai_bp)
    app.register_blueprint(admin_ai_config_bp)

    @app.errorhandler(Exception)
    def handle_exception(e):
        if isinstance(e, HTTPException):
            return {"error": e.name, "details": e.description}, e.code

        app.logger.error(f"Unhandled exception: {str(e)}", exc_info=True)
        return {"error": "Internal Server Error", "details": str(e)}, 500

    @app.shell_context_processor
    def make_shell_context():
        from models.cultural_resource import CulturalResource
        from models.knowledge import KnowledgeCategory, KnowledgeNode, KnowledgeRelationship
        from models.user import User
        from models.ai_config import AIConfig
        from models.conversation import Conversation, Message

        return {"db": db, "User": User, "CulturalResource": CulturalResource,
                "KnowledgeCategory": KnowledgeCategory, "KnowledgeNode": KnowledgeNode,
                "KnowledgeRelationship": KnowledgeRelationship,
                "AIConfig": AIConfig, "Conversation": Conversation, "Message": Message}

    return app
