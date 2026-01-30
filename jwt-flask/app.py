from flask import Flask
from models import db
from routes.presence_start import bp as start_bp
from routes.presence_verify import bp as verify_bp
from config import SQLALCHEMY_DATABASE_URI

def create_app():
    app = Flask(__name__)

    app.config["SQLALCHEMY_DATABASE_URI"] = SQLALCHEMY_DATABASE_URI
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    db.init_app(app)

    with app.app_context():
        db.create_all()

    app.register_blueprint(start_bp)
    app.register_blueprint(verify_bp)

    return app


if __name__ == "__main__":
    app = create_app()
    app.run(debug=True)