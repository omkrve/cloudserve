
import click
from flask import Flask
from flask_login import LoginManager
from flask_wtf.csrf import CSRFProtect
from werkzeug.security import check_password_hash

from config import Config
from app.models import User, db

login_manager = LoginManager()
csrf = CSRFProtect()


@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))


def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_object(Config)

    if test_config:
        app.config.update(test_config)

    db.init_app(app)
    login_manager.init_app(app)
    csrf.init_app(app)

    login_manager.login_view = "auth.login"
    login_manager.login_message_category = "error"

    from app.routes.main import main
    from app.routes.auth import auth

    app.register_blueprint(main)
    app.register_blueprint(auth)

    with app.app_context():
        db.create_all()

    @app.cli.command("create-admin")
    def create_admin():
        """Create the first administrator account."""
        email = click.prompt("Administrator email").strip().lower()
        name = click.prompt("Administrator name").strip()
        password = click.prompt(
            "Administrator password", hide_input=True,
            confirmation_prompt=True
        )

        if not email or not name or len(password) < 12:
            raise click.ClickException(
                "Provide a name, email, and password of at least 12 characters."
            )

        if User.query.filter_by(email=email).first():
            raise click.ClickException("That email is already registered.")

        admin = User(name=name, email=email, role="admin")
        admin.set_password(password)
        db.session.add(admin)
        db.session.commit()
        click.echo("Administrator account created.")

    return app
