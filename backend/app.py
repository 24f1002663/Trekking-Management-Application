from flask import Flask
from model import db, user
from routes.authentication import auth_bp
from routes.pages import pages_bp
from werkzeug.security import generate_password_hash
from flask_jwt_extended import JWTManager


def create_app():

    app = Flask(__name__)

    app.static_folder = "../frontend/static"
    app.static_url_path = "/static"

    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///trek.db"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    app.config["SECRET_KEY"] = "trek-management-secret-key-2024-flask"
    app.config["JWT_SECRET_KEY"] = "trek-management-jwt-secret-key-2024-secure"

    db.init_app(app)

    JWTManager(app)

    app.register_blueprint(auth_bp, url_prefix="/auth")
    app.register_blueprint(pages_bp)

    return app


def create_admin():

    admin = user.query.filter_by(role="admin").first()

    if admin is None:

        new_admin = user(
            name="Administrator",
            email="admin@trek.com",
            password=generate_password_hash("admin123"),
            role="admin",
            status="active",
            gender="Female"
        )

        db.session.add(new_admin)
        db.session.commit()


app = create_app()

with app.app_context():
    db.create_all()
    create_admin()

if __name__ == "__main__":
    app.run(debug=True, port=8080, use_reloader=False)