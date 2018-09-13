from datetime import datetime
from flask import current_app
from . import db



class APScheduleJob(db.Model):
    __tablename__ = 'jobs'
    id = db.Column(db.Integer, primary_key=True)
    jobid = db.Column(db.String(64), unique=True, index=True)
    jobfunction = db.Column(db.String(64))
    jobname = db.Column(db.String(64))
    jobtrigger = db.Column(db.String(64))
    jobseconds = db.Column(db.Integer)
    jobruntimes = db.Column(db.Integer)
    jobargs = db.Column(db.Text())
    append_time = db.Column(db.DateTime(), default=datetime.utcnow)

    def __init__(self, **kwargs):
        super(APScheduleJob, self).__init__(**kwargs)

    def register_time(self):
        self.append_time = datetime.utcnow()
        db.session.add(self)
    def add_run_time(self):
        self.jobruntimes = self.jobruntimes + 1 #?
        db.session.add(self) 

    def __repr__(self):
        return '<Job %r>' % self.jobid




class User(db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50))
    password = db.Column(db.String(50))

    def __init__(self, **kwargs):
        super(User, self).__init__(**kwargs)

    def __repr__(self):
        return '<User %r>' % self.username

