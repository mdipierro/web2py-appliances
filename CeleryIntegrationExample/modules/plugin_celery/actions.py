import sys, os
sys.path.append(os.path.dirname(__file__))
from celery.app import default_app
from celery.utils import get_full_cls_name
from celery.registry import tasks
from celery.execute import send_task
from celery.result import AsyncResult
from celery.task import control
from celery.task.base import TaskType
from plugin_celery import tasks as mytasks

def istask(obj):
    try:
        return obj.__class__ == TaskType
    except AttributeError:
        return False

def get_task_names():
    return ['tasks.'+name for name in dir(mytasks) if istask(getattr(mytasks,name))]

def submit_task(name,*args,**vars):
    """ submits a new task by name """
    print args, vars
    result = send_task(name,args=args,kwargs=vars)
    return {"ok": "true", "task_id": result.task_id}

def registered_tasks():
    """ returns registered tasks """
    return {"regular": tasks.regular().keys(),
            "periodic": tasks.periodic().keys()}

def task_status(task_id):
    """ returns task status and result """
    status = default_app.backend.get_status(task_id)
    res = default_app.backend.get_result(task_id)
    response_data = dict(id=task_id, status=status, result=res)
    if status in default_app.backend.EXCEPTION_STATES:
        traceback = default_app.backend.get_traceback(task_id)
        response_data.update({"result": repr(res),
                              "exc": get_full_cls_name(res.__class__),
                              "traceback": traceback})
    return {"task": response_data}

def revoke_task(task_id,terminate=False,signal=None):
    connection = default_app.broker_connection()
    return control.revoke(task_id, connection=connection,
                  terminate=terminate, signal=signal)

def terminate_task(task_id):
    return revoke_task(task_id,terminate=True)

def kill_task(task_id):
    return revoke_task(task_id,terminate=True,signal='KILL')

def list_workers(timeout=0.5):
    return [item.keys()[0] for item in control.ping(timeout=timeout)]

def inspect_workers(workers):
    i = control.inspect(workers)
    return {
        'registered_tasks':i.registered_tasks(),
        'active':i.active(),
        'scheduled':i.scheduled(),
        'reserved':i.reserved()}

def shutdown_workers(workers):
    return control.broadcast('shutdown', destination=workers)

def set_time_limit(task_name, soft=60, hard=120, reply=True):
    return control.time_limit(task_name,soft,hard,reply)

def set_rate_limit(task_name,rate_limit,workers=None):
    return control.broadcast("rate_limit", 
                             {"task_name": "myapp.mytask",
                              "rate_limit": "200/m"}, reply=True,
                             destination=workers)

def main_test():
    import sys
    import time
    if len(sys.argv)<2 or sys.argv[1] in ('-h','--help','-help','help'):
        print """
Module to be imported from controller to perform basic actions
Can also be used interactively from shell
usage:
        %(name)s demo
        %(name)s registered_tasks
        %(name)s submit_task <name>
        %(name)s task_status <id>
        (for demo <name> is 'tasks.DemoTaskFast' or 'tasks.DemoTaskSlow')
        """ % dict(name=sys.argv[0])
    elif sys.argv[1]=='submit_task':
        task = submit_task(sys.argv[2])
        print task['task_id']
    elif sys.argv[1]=='task_status' and len(sys.argv)>2:
        status = task_status(sys.argv[2])
        print status
    elif sys.argv[1]=='registered_tasks':
        print registered_tasks() 
    elif sys.argv[1] == 'demo':
        print registered_tasks()
        task = submit_task('tasks.DemoTaskFast')        
        from time import sleep
        while True:
            status = task_status(task['task_id'])    
            print status
            if status['task']['status']==u'SUCCESS': break
            sleep(1)
    else:
        print 'try: %s help' % sys.argv[0]

if __name__=='__main__':    
    main_test()
