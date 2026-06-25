import pytest
from flask import Blueprint, Flask

from app.auth import admin_required, login_required


@pytest.fixture
def client():
    app = Flask(__name__)
    app.secret_key = "test_secret_key"

    auth = Blueprint("auth", __name__)

    @auth.route("/login")
    def login():
        return "Login Page"

    @auth.route("/dashboard")
    def dashboard():
        return "Dashboard"

    @auth.route("/home")
    @login_required
    def home():
        return "Home"

    @auth.route("/admin")
    @admin_required
    def admin():
        return "Admin"

    app.register_blueprint(auth)

    with app.test_client() as client:
        yield client


def test_locked_page_redirects_a_guest(client):
    response = client.get("/home")

    assert response.status_code == 302
    assert "login" in response.location


def test_locked_page_allows_logged_in_user(client):
    with client.session_transaction() as sess:
        sess["user_id"] = 1

    response = client.get("/home")

    assert response.status_code == 200
    assert response.data == b"Home"


def test_admin_page_redirects_regular_user(client):
    with client.session_transaction() as sess:
        sess["user_id"] = 1
        sess["user_role"] = "user"

    response = client.get("/admin")

    assert response.status_code == 302
    assert "dashboard" in response.location


def test_admin_page_allows_admin_user(client):
    with client.session_transaction() as sess:
        sess["user_id"] = 1
        sess["user_role"] = "admin"

    response = client.get("/admin")

    assert response.status_code == 200
    assert response.data == b"Admin"


def test_logout_style_session_can_be_cleared(client):
    with client.session_transaction() as sess:
        sess["user_id"] = 1
        sess["user_name"] = "Test User"

    with client.session_transaction() as sess:
        sess.clear()

    with client.session_transaction() as sess:
        assert "user_id" not in sess
        assert "user_name" not in sess
