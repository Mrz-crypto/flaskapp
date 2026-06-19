import pytest
from flask import Blueprint, Flask

from app.auth import login_required


@pytest.fixture
def client():
    app = Flask(__name__)
    app.secret_key = "test_secret_key"

    auth = Blueprint("auth", __name__)

    @auth.route("/login")
    def login():
        return "Login Page"

    @auth.route("/home")
    @login_required
    def home():
        return "swagatam"

    app.register_blueprint(auth)

    with app.test_client() as client:
        yield client


def test_locked_page_redirects_a_guest(client):
    """A guest should be redirected to the login page."""
    response = client.get("/home")

    assert response.status_code == 302
    assert "login" in response.location
