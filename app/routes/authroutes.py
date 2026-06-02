from flask import Blueprint
from app.controllers import authcontroller

auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/")
def home():
    return authcontroller.home()


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    return authcontroller.login()


@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    return authcontroller.register()


@auth_bp.route("/dashboard", methods=["GET", "POST"])
def dashboard():
    return authcontroller.dashboard()


@auth_bp.route("/logout")
def logout():
    return authcontroller.logout()


def register():
    return auth_bp
