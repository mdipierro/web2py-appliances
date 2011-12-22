import sys
import os
import optparse

sys.path.append(os.getcwd())

from celery.bin import camqadm, celeryev, celerybeat, celeryd, celeryd_detach
from celery.bin.celeryctl import celeryctl, Command as _Command
from celery.app import default_app
print """
Warning... this file is here for compatibility with django-celery but it is
not necessay: manage.py [whatever...] is the same as just [whatever...].
"""
try:
    from celerymonitor.bin.celerymond import MonitorCommand
    monitor = MonitorCommand(app=default_app)
except ImportError:
    monitor = None
    MISSING = """                      
You don't have celerymon installed, please install it by running the following command:                                                              
    $ pip install -U celerymon                                   
or if you're still using easy_install (shame on you!)
    $ easy_install -U celerymon
"""


command = camqadm.AMQPAdminCommand(app=default_app)
ev = celeryev.EvCommand(app=default_app)
beat = celerybeat.BeatCommand(app=default_app)
util = celeryctl(app=default_app)
worker = celeryd.WorkerCommand(app=default_app)
class detached(celeryd_detach.detached_celeryd):
    execv_argv = [os.path.abspath(sys.argv[0]), "celeryd"]

OPTIONS = {
    'camqadm':(
        'Celery AMQP Administration Tool using the AMQP API.',
        command.get_options(),
        lambda args,options: command.run(*args, **options)),
    'celerybeat':(
        'Runs the Celery periodic task scheduler',
        beat.get_options(),
        lambda args,options: beat.run(*args, **options)),
    'celeryctl':(
        "celery control utility",
        [],
        lambda args,options: util.execute_from_commandline(sys.argv[3:])),
    'celeryd':(
        'Runs a Celery worker node.',
        worker.get_options(),
        lambda args,options: worker.run(*args, **options)),
    'celeryd_detach':(
        'Runs a detached Celery worker node.',
        celeryd_detach.OPTION_LIST,
        lambda args,options: detached().execute_from_commandline(sys.argv)),
    'celeryd_multi':(
        "Manage multiple Celery worker nodes.",
        ["[name1, [name2, [...]> [worker options]"],
        lambda args,options: (
            argv.append("--cmd=%s celeryd_detach" % (argv[0], )),
            celeryd_multi.MultiTool().execute_from_commandline(
                ["%s %s" % (sys.argv[0], sys.argv[1])] + sys.argv[2:]))),
    'celeryev':(
        'curses celery event viewer',
        ev.get_options(),
        lambda args,options: ev.run(*args, **options)),
    'celerymon':(
        'Run the celery monitor',
        (monitor and monitor.get_options() or []),
        lambda args,options: \
            monitor and monitor.run(**options) or sys.stderr.write(MISSING))}

def main():
    try:
        help,option_list,f = OPTIONS[sys.argv[1]]
    except:
        for key,(help,option_list,f) in OPTIONS.items():
            print '%s %s (%s)' % (sys.argv[0],key,help)
    else:
        parser = optparse.OptionParser(option_list=option_list)
        del sys.argv[1]
        (options,args) = parser.parse_args()
        print args
        print options.__dict__
        return f(args,options.__dict__)

main()
