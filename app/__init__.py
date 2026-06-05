import logging
from flask import Flask, render_template
import config
from app.database import create_tables

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def create_app():
    app = Flask(__name__)
    app.secret_key = config.SECRET_KEY
    app.config['DEBUG'] = config.DEBUG

    logger.info(f"Creating Flask app in {config.FLASK_ENV} mode")

    with app.app_context():
        create_tables()

    from app.routes.authroutes import register_blueprint as register_auth
    from app.routes.orderroutes import register_blueprint as register_orders

    app.register_blueprint(register_auth())
    app.register_blueprint(register_orders())

    logger.info("Blueprints registered successfully")

    @app.errorhandler(403)
    def forbidden(e):
        logger.warning(f"403 Forbidden error: {e}")
        return render_template("403.html"), 403

    @app.errorhandler(404)
    def page_not_found(e):
        logger.warning(f"404 Not Found error: {e}")
        return render_template("404.html"), 404

    @app.errorhandler(500)
    def internal_error(e):
        logger.error(f"500 Internal Server Error: {e}")
        return render_template("500.html"), 500

    return app
