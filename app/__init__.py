from flask import Flask, render_template
import config
from app.database import create_tables


def create_app():
    app = Flask(__name__)
    app.secret_key = config.SECRET_KEY

    with app.app_context():
        create_tables()

    from app.routes.authroutes import register as register_auth
    from app.routes.orderroutes import register as register_orders

    app.register_blueprint(register_auth())
    app.register_blueprint(register_orders())

    @app.errorhandler(403)
    def forbidden(e):
        return render_template("403.html"), 403

    @app.errorhandler(404)
    def page_not_found(e):
        return render_template("404.html"), 404

    @app.errorhandler(500)
    def internal_error(e):
        return render_template("500.html"), 500

    return app
