
import pytest

from app import create_app
from app.models import db, User


@pytest.fixture
def app():
    app = create_app({
        "TESTING": True,
        "SECRET_KEY": "test-secret-key",
        "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",
        "WTF_CSRF_ENABLED": False,
    })

    with app.app_context():
        db.drop_all()
        db.create_all()

        yield app

        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def user(app):
    with app.app_context():
        account = User(
            name="Demo User",
            email="user@example.com",
            role="user",
        )
        account.set_password("TestPassword123!")
        db.session.add(account)
        db.session.commit()
        return account.id


@pytest.fixture
def admin(app):
    with app.app_context():
        account = User(
            name="Demo Admin",
            email="admin@example.com",
            role="admin",
        )
        account.set_password("AdminPassword123!")
        db.session.add(account)
        db.session.commit()
        return account.id
