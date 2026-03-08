from flask import Flask, Response
from models import db
import models.proof  # noqa: F401
import models.session  # noqa: F401
import models.pi_status  # noqa: F401
import models.pi_key  # noqa: F401
from routes.presence_exchange import bp as exchange_bp
from routes.admin_pi import bp as admin_pi_bp
from config import SQLALCHEMY_DATABASE_URI

def create_app():
    app = Flask(__name__)
    app.config["SQLALCHEMY_DATABASE_URI"] = SQLALCHEMY_DATABASE_URI
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    db.init_app(app)

    with app.app_context():
        db.create_all()

    @app.get("/")
    def homepage():
        html = (
            "<html><head><title>JWT Verification Service</title>"
            "<style>"
            "body{font-family:Arial,sans-serif;margin:32px;max-width:960px;line-height:1.5;color:#1f2937;}"
            "h1{margin-bottom:8px;}h2{margin-top:28px;margin-bottom:10px;}"
            "code{background:#f3f4f6;padding:2px 6px;border-radius:4px;}"
            "table{border-collapse:collapse;width:100%;margin-top:12px;}"
            "th,td{border:1px solid #d1d5db;padding:10px;vertical-align:top;text-align:left;}"
            "th{background:#f9fafb;}a{color:#0f766e;text-decoration:none;}a:hover{text-decoration:underline;}"
            "</style></head><body>"
            "<h1>JWT Verification Service</h1>"
            "<p>This service supports the current Pi-backed JWT presence flow. "
            "The endpoints below are the active paths exposed by the Flask app.</p>"
            "<h2>Active Endpoints</h2>"
            "<table>"
            "<tr><th>Method</th><th>Path</th><th>What it does</th></tr>"
            "<tr><td>GET</td><td><code>/admin</code></td><td>Shows the Pi connection dashboard as HTML, including online status, bridge URL, last challenge, and last exchange times.</td></tr>"
            "<tr><td>GET</td><td><code>/admin/pis</code></td><td>Returns Pi status data as JSON for admin/monitoring use.</td></tr>"
            "<tr><td>POST</td><td><code>/presence/pi/heartbeat</code></td><td>Accepts Pi heartbeat updates so the backend can track reachability and bridge connectivity.</td></tr>"
            "<tr><td>POST</td><td><code>/presence/pi/register</code></td><td>Registers or updates a Pi public key used later for signature verification.</td></tr>"
            "<tr><td>GET</td><td><code>/presence/pi/resolve</code></td><td>Returns the currently available Pi bridge URL for a requested Pi, or the most recent online Pi if none is specified.</td></tr>"
            "<tr><td>GET</td><td><code>/presence/challenge</code></td><td>Fetches a signed challenge packet from a Pi bridge through the backend and returns the challenge, Pi ID, and Pi signature.</td></tr>"
            "<tr><td>POST</td><td><code>/presence/exchange</code></td><td>Verifies the Pi signature and user signature for a challenge, then issues and stores a JWT presence session.</td></tr>"
            "</table>"
            "<h2>Notes</h2>"
            "<p>Older development routes exist in the repository, but only the paths listed above are mounted in the current application.</p>"
            "<p>Admin endpoints may require a token depending on deployment configuration.</p>"
            "</body></html>"
        )
        return Response(html, mimetype="text/html")

    app.register_blueprint(exchange_bp)
    app.register_blueprint(admin_pi_bp)

    return app

if __name__ == "__main__":
    app = create_app()
    app.run(debug=True)
