from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from .config import Config
from datetime import datetime

db = SQLAlchemy()
migrate = Migrate()
from . import models

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    migrate.init_app(app, db)

    # Import models so migrations can see them
    from . import models

    # Register blueprints
    from . import routes, auth, billing
    app.register_blueprint(routes.bp)
    app.register_blueprint(auth.bp)
    app.register_blueprint(billing.bp)

    # Jinja globals
    @app.context_processor
    def inject_globals():
        return {"current_year": datetime.utcnow().year}

    @app.route("/health")
    def health():
        return "ok", 200

    return app
