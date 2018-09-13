# carnation 康乃馨 
# 
1. install virtual env 
   #virtualenv venv
   #source  venv/bin/activate
2. install package
   (venv)#pip install flask
   (venv)#pip install flask-script
   (venv)#pip install flask-bootstrap
   (venv)#pip install flask-wtf
   (venv)#pip install flask-sqlalchemy
   (venv)#pip install flask-migrate
   (venv)#pip install flask-mail
   (venv)#pip install mysql-python
   (venv)#pip install Flask-APScheduler


3. database: carnation
   CREATE DATABASE IF NOT EXISTS carnation DEFAULT CHARSET utf8 COLLATE utf8_general_ci


4. structure
   #tree -I 'venv|migrations|*.pyc'
   .
   ├── app
   │   ├── __init__.py
   │   ├── main
   │   │   ├── errors.py
   │   │   ├── __init__.py
   │   │   └── views.py
   │   └── templates
   │       ├── 404.html
   │       ├── 500.html
   │       ├── base.html
   │       └── index.html
   ├── config.py
   ├── jobs.py
   ├── manage.py
   └── README.md

5. run
   #python manage.py runserver -h 0.0.0.0

6. apscheduler use
   1). define job config in config.py
   2). init and start in app/__init__.py
   3). after flask run, test job will print at terminal and scheduler api can be use
   4). api
           address                                method     return value
    http://192.168.0.107:5000/scheduler            get        
	 {"current_host": "virtualbox", "allowed_hosts": ["*"], "running": true}
    http://192.168.0.107:5000/scheduler/jobs       get
    [
	  {
	    "id": "job1", 
		"name": "job1", 
		"func": "jobs:job1", 
		"args": [1, 2], 
		"kwargs": {}, 
		"trigger": "interval", 
		"start_date": "2018-09-12T15:36:04.647100+08:00", 
		"seconds": 10, 
		"misfire_grace_time": 1, 
		"max_instances": 1, 
		"next_run_time": "2018-09-12T15:37:44.647100+08:00"
	  }
   ]
   //it show all jobs that are running, not include the finished job. 
   http://192.168.0.107:5000/scheduler/jobs/<job_id>  get 
   http://192.168.0.107:5000/scheduler/jobs  post(add job)
   {"id":"job2","func":"jobs:job1","name":"job2","args": [202, 303]}      // this job only be runned once.
   {"id":"job3","func":"jobs:job1","name":"job3","trigger":"interval","args": [802, 903]} //this job be runned every one second
   {"id":"job3","func":"jobs:job1","name":"job3","seconds": 10, "trigger":"interval","args": [802, 903]} //this job be runned every ten seconds
   http://192.168.0.107:5000/scheduler/jobs/job3 delete(remove job) return 204

7. http post
   1) utils.py
   2) define job2 in jobs.py, when send message to http://192.168.0.107:5000/scheduler/jobs, {"id":"job2","func":"jobs:job2","name":"job2"}. it only be excuted once.

    
8. error:
   log:No handlers could be found for logger "apscheduler.executors.default"
   fix:import logging
       logging.basicConfig()

9. add mysql password in activate script
10. use database to store job
    SCHEDULER_JOBSTORES = {
        'default': SQLAlchemyJobStore(url=Config.SQLALCHEMY_DATABASE_URI)
    }
    default, APScheduler use memory to store job, use database to store job, it only store running job, and if flask restart, it will show error: apscheduler.jobstores.base.ConflictingIdError: u'Job identifier (job1) conflicts with an existing job', I must clean table using next command: truncate table apscheduler_jobs;


