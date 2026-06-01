from flask import Flask
from model import db, user
from werkzeug.security import generate_password_hash


def create_app():

    app = Flask(__name__)

    app.static_folder = "../frontend/static"
    app.static_url_path = "/static"

    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///trek.db"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    db.init_app(app)

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