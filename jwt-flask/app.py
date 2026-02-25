from flask import Flask
from models import db
import models.proof  # noqa: F401
import models.session  # noqa: F401
from routes.presence_exchange import bp as exchange_bp
from config import SQLALCHEMY_DATABASE_URI

def create_app():
    app = Flask(__name__)
    app.config["SQLALCHEMY_DATABASE_URI"] = SQLALCHEMY_DATABASE_URI
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    db.init_app(app)

    with app.app_context():
        db.create_all()

    app.register_blueprint(exchange_bp)

    return app

if __name__ == "__main__":
    app = create_app()
    app.run(debug=True)