from .models import APScheduleJob
from .models import User
from . import scheduler
from . import db
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

def save_events(events):
    with scheduler.app.app_context():
        #print("app_context")
        job = APScheduleJob.query.filter_by(jobid=events.job_id).first()
        if job is None:
            #print("job is not , init it")
            job = APScheduleJob(jobid=events.job_id, jobruntimes = 0, jobname=events.job_id)
            job.add_run_time()
            db.session.add(job)
            #test user
            user = User(username='john',password='cat')
            db.session.add(user)
            db.session.commit()

        else:
            #print("job exist, update")
            job.add_run_time()
            db.session.add(job)
            db.session.commit()

def event_listener(events):
    if events.code == EVENT_JOB_MISSED:
        print("Job missed id in: %s " % str(events.job_id))
        save_events(events)
    elif events.code == EVENT_JOB_EXECUTED:
        print("Job execute is %s " % str(events.job_id))
        save_events(events)

