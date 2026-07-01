from flask import Flask
from dotenv import load_dotenv

from .config import Config
from .db import init_db


def create_app():
    load_dotenv()

    app = Flask(__name__)
    app.config.from_object(Config)

    init_db(app)

    from .routes.dashboard import bp as dashboard_bp
    from .routes.medications import bp as medications_bp
    from .routes.sales import bp as sales_bp
    from .routes.forecast import bp as forecast_bp

    app.register_blueprint(dashboard_bp)
    app.register_blueprint(medications_bp)
    app.register_blueprint(sales_bp)
    app.register_blueprint(forecast_bp)

    return app
