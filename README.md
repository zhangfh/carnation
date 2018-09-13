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

11. create table
   1)create table and model APScheduleJob
   2)use model in manage.db
   3) python manage.py db init
      python manage.py db migrate -m "init"
      python manage.py db upgrade
      it cannot create database now.
      #python manage.py  shell
      >>> db.create_all()        #after this command, table 'jobs' is created

12. add listener for APScheduler
    scheduler.add_listener(event_listener, LISTENER_JOB)
    
13. save event to jobs table
    please note : 1) import position
                  2) with context
 
14. move code structure
    .
    ├── app
    │   ├── events.py
    │   ├── __init__.py
    │   ├── jobs.py
    │   ├── main
    │   │   ├── errors.py
    │   │   ├── __init__.py
    │   │   └── views.py
    │   ├── models.py
    │   ├── templates
    │   │   ├── 404.html
    │   │   ├── 500.html
    │   │   ├── base.html
    │   │   └── index.html
    │   └── utils.py
    ├── config.py
    ├── manage.py
    └── README.md
    jobs, events, utils are placed under app directory

    jobs be used by app. , for example:        
    'func': 'app.jobs:job1',
    add new job:
    {"id":"job2","func":"app.jobs:job1","name":"job2","args": [202, 303]} 
15. app/utils get_hostname()
16. config host allowed
17. config max instance
18. cron
    add job, post data to http://192.168.0.107:5000/scheduler/jobs
    {
	"id":"job3",
	"func":"app.jobs:job1",
	"name":"job3",
	"second": "*/10", 
	"hour": "*",
	"trigger":"cron",
	"args": [702, 603]
    }
    parameters:

        'year'
        'month'
        'week'
        'day'
        'day_of_week'
        'hour'
        'minute'
        'second'
     Cron rules:
	Expression	Field	Description
	*		any	Fire on every value
	*/a		any	Fire every a values, starting from the minimum
	a-b		any	Fire on any value within the a-b range (a must be smaller than b)
	a-b/c		any	Fire every c values within the a-b range
	xth y		day	Fire on the x -th occurrence of weekday y within the month
	last x		day	Fire on the last occurrence of weekday x within the month
	last		day	Fire on the last day within the month
	x,y,z		any	Fire on any matching expression; can combine any number of any of the above expressions

	(int|str) 表示参数既可以是int类型，也可以是str类型
	(datetime | str) 表示参数既可以是datetime类型，也可以是str类型
 
	year (int|str) – 4-digit year -（表示四位数的年份，如2008年）
	month (int|str) – month (1-12) -（表示取值范围为1-12月）
	day (int|str) – day of the (1-31) -（表示取值范围为1-31日）
	week (int|str) – ISO week (1-53) -（格里历2006年12月31日可以写成2006年-W52-7（扩展形式）或2006W527（紧凑形式））
	day_of_week (int|str) – number or name of weekday (0-6 or mon,tue,wed,thu,fri,sat,sun) - （表示一周中的第几天，既可以用0-6表示也可以用其英语缩写表示）
	hour (int|str) – hour (0-23) - （表示取值范围为0-23时）
	minute (int|str) – minute (0-59) - （表示取值范围为0-59分）
	second (int|str) – second (0-59) - （表示取值范围为0-59秒）
	start_date (datetime|str) – earliest possible date/time to trigger on (inclusive) - （表示开始时间）
	end_date (datetime|str) – latest possible date/time to trigger on (inclusive) - （表示结束时间）
timezone (datetime.tzinfo|str) – time zone to use for the date/time calculations (defaults to scheduler timezone) -（表示时区取值）
19. Flask-AQScheduler auth
20. Requirement
    pip freeze > requirements.txt
21. disable job in config.py
22. table is exist, how to use it:
    1)create user table
    mysql>>>create table user(id int(12) not null auto_increment, username varchar(50) default null, password varchar(50) not null, primary key(id);
    2)create user model 
    3) use it events.py
23. use log
    1) mkdir log directory
    2) log.py
    3) using logging

24. Once add a job, the same job cannot be add again.

