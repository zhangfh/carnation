import os
#from flask_migrate import Migrate
from app import create_app, db
from app.models import APScheduleJob
from flask_script import Manager,Shell
from flask_migrate import Migrate, MigrateCommand
import log
import logging

#app = create_app(os.getenv('FLASK_CONFIG') or 'default')
app = create_app(os.getenv('FLASK_CONFIG') or 'job')
#migrate = Migrate(app, db)
manager = Manager(app)
migrate = Migrate(app,db)

def make_shell_context():
    return dict(app=app, db=db, APSJOB=APScheduleJob)
manager.add_command("shell",Shell(make_context=make_shell_context))
manager.add_command("db",MigrateCommand)

#@app.cli.command()
@manager.command
def test():
    """Run the unit tests."""
    import unittest
    tests = unittest.TestLoader().discover('tests')
    unittest.TextTestRunner(verbosity=2).run(tests)

if __name__ == '__main__':
    log.init_log('./log/logging.txt')
    logging.info('logging starts')
    #app.run(debug=True,host='0.0.0.0')
    manager.run()

