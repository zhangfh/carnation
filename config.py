from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore
import os

basedir = os.path.abspath(os.path.dirname(__file__))

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'Wtf012'

    mysql_password = os.getenv('FLASK_MYSQL_PASSWORD') or 'default'
    mysql_url = 'mysql://root:' + mysql_password + '@localhost/carnation'
    SQLALCHEMY_DATABASE_URI = mysql_url
    SQLALCHEMY_COMMIT_ON_TEARDOWN = True

    MAIL_SERVER = 'smtp.163.com'
    MAIL_PORT = 465
    MAIL_USE_SSL = True
    MAIL_USERNAME = os.environ.get('FLASK_MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('FLASK_MAIL_PASSWORD')
    FLASKY_MAIL_SUBJECT_PREFIX = '[Register]'
    FLASKY_MAIL_SENDER = os.environ.get('FLASK_MAIL_SENDER')
    FLASKY_ADMIN = os.environ.get('FLASK_ADMIN')


    @staticmethod
    def init_app(app):
        pass

class DevelopmentConfig(Config):
    DEBUG = True
    @staticmethod
    def init_app(app):
        print("DevelopmentConfig init_app")
 
class TestingConfig(Config):
    TESTING = True

class ProductionConfig(Config):
    PRODUCTION = True

class JobConfig(Config):
    JOB = True
    JOBS = [
        {
            'id': 'job1',
            'func': 'jobs:job1',
            'args': (1, 2),
            'trigger': 'interval',
            'seconds': 10
        }
    ]
    #SCHEDULER_JOBSTORES = {
    #    'default': SQLAlchemyJobStore(url=Config.SQLALCHEMY_DATABASE_URI)
    #}
    SCHEDULER_API_ENABLED = True

config = {
    'development' : DevelopmentConfig,
    'testing' : TestingConfig,
    'production' : ProductionConfig,
    'default' : DevelopmentConfig,
    'job'  :  JobConfig
}
