from flask import Flask
from flask_bootstrap import Bootstrap
from flask_mail import Mail
from flask_sqlalchemy import SQLAlchemy
from config import config
from flask_apscheduler import APScheduler


bootstrap = Bootstrap()
mail = Mail()
db = SQLAlchemy()
scheduler = APScheduler()

def create_app(config_name):
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    config[config_name].init_app(app)

    bootstrap.init_app(app)
    mail.init_app(app)
    db.init_app(app)
    scheduler.init_app(app)
    scheduler.start()

    from .main import main as main_blueprint
    app.register_blueprint(main_blueprint)


    return app

