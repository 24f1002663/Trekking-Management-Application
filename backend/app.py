from flask import Flask
from model import db, user
from routes.authentication import auth_bp
from routes.admin import admin_bp
from routes.staff import staff_bp
from routes.pages import pages_bp
from werkzeug.security import generate_password_hash
from flask_jwt_extended import JWTManager
from flask_cors import CORS
from mail_service import mail
import os


def create_app():

    app = Flask(__name__)

    app.static_folder = "../frontend/static"
    app.static_url_path = "/static"

    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///trek.db"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    app.config["SECRET_KEY"] = "trek-management-secret-key-2024-flask"
    app.config["JWT_SECRET_KEY"] = "trek-management-jwt-secret-key-2024-secure"

    app.config["UPLOAD_FOLDER"] = os.path.join(
        os.path.dirname(__file__),
        "..",
        "frontend",
        "static",
        "uploads"
    )

    if not os.path.exists(app.config["UPLOAD_FOLDER"]):
        os.makedirs(app.config["UPLOAD_FOLDER"])

    mail_user = os.environ.get("MAIL_USERNAME", "")
    mail_pass = os.environ.get("MAIL_PASSWORD", "")

    app.config["MAIL_SERVER"] = "smtp.gmail.com"
    app.config["MAIL_PORT"] = 587
    app.config["MAIL_USE_TLS"] = True
    app.config["MAIL_USE_SSL"] = False
    app.config["MAIL_USERNAME"] = mail_user
    app.config["MAIL_PASSWORD"] = mail_pass
    app.config["MAIL_DEFAULT_SENDER"] = mail_user or "Trek Management"

    if mail_user:
        print(f"[Mail] Configured — sending from: {mail_user}")
    else:
        print("[Mail] WARNING: MAIL_USERNAME not set. Set env var before starting.")
        print("[Mail] Example: $env:MAIL_USERNAME='your@email.com'; $env:MAIL_PASSWORD='app_password'")

    db.init_app(app)
    mail.init_app(app)

    JWTManager(app)
    CORS(app)

    app.register_blueprint(auth_bp, url_prefix="/auth")
    app.register_blueprint(admin_bp, url_prefix="/admin")
    app.register_blueprint(staff_bp, url_prefix="/staff")
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