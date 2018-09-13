from flask import Flask
from flask_bootstrap import Bootstrap
from flask_mail import Mail
from flask_sqlalchemy import SQLAlchemy
from config import config
from flask_apscheduler import APScheduler
from apscheduler.events import *
from flask import current_app
#import logging

#logging.basicConfig()
#logging.getLogger('apscheduler').setLevel(logging.DEBUG)

#from .models import APScheduleJob #compile error

from apscheduler.events import *


#EVENT_JOB_ADDED = 128
#EVENT_JOB_REMOVED = 256
#EVENT_JOB_MODIFIED = 512
#EVENT_JOB_EXECUTED = 1024
#EVENT_JOB_ERROR = 2048
#EVENT_JOB_MISSED = 4096#

LISTENER_JOB = (EVENT_JOB_ADDED |
                EVENT_JOB_REMOVED |
                EVENT_JOB_MODIFIED |
                EVENT_JOB_EXECUTED |
                EVENT_JOB_ERROR |
                EVENT_JOB_MISSED)




bootstrap = Bootstrap()
mail = Mail()
db = SQLAlchemy()
scheduler = APScheduler()

from events import event_listener

def create_app(config_name):
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    config[config_name].init_app(app)

    bootstrap.init_app(app)
    mail.init_app(app)
    db.init_app(app)
    scheduler.init_app(app)
    scheduler.add_listener(event_listener, LISTENER_JOB)
    scheduler.start()

    from .main import main as main_blueprint
    app.register_blueprint(main_blueprint)


    return app

