from flask import Flask
from flask_cors import CORS

from routes.plan_routes import plan_bp
from routes.quiz_routes import quiz_bp


def create_app() -> Flask:
    app = Flask(__name__)
    CORS(app)

    app.register_blueprint(plan_bp, url_prefix="/api/plan")
    app.register_blueprint(quiz_bp, url_prefix="/api/quiz")

    return app


if __name__ == "__main__":
    app = create_app()
    app.run(host="0.0.0.0", port=5000, debug=True)

