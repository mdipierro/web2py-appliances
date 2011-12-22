from gluon.serializers import json
from plugin_celery import actions

class TYPE(object):
    def __init__(self,myclass=list,parse=True):
        self.myclass = myclass
        self.parse=parse
    def __call__(self,value):
        from gluon.contrib.simplejson import loads
        try:
            obj = loads(value)
        except:
            return (value,T('invalid json'))
        else:
            if isinstance(obj,self.myclass):
                if self.parse:
                    return (obj,None)
                else:
                    return (value,None)
            else:
                return (value,'Not of type: %s' % self.myclass)

response.menu += [
    (T('Celery Console'),False,None,[
            (T('New Task'),False,URL('create_task')),
            (T('Task Monitor (Meta)'),False,URL('task_monitor')),
            (T('Task Monitor (Camera)'),False,URL('taskstate_monitor')),
            (T('Task Schduler'),False,URL('periodictask_monitor')),
            (T('Workers Monitor'),False,URL('workers_monitor'))])]

TASKS = actions.get_task_names()

pc = plugin_celery
db = plugin_celery.db

def index():
    redirect(URL('taskstate_monitor'))

def submit_task():
    name = request.args(0)
    args = request.args[1:]
    vars = request.vars
    response.headers['Content-Type'] = "application/json"
    return json(actions.submit_task(name,*args,**vars))

def create_task():
    form = SQLFORM.factory(Field('task',requires=IS_IN_SET(TASKS)),
                           Field('args',default='[]',requires=TYPE(list)),
                           Field('vars',default='{}',requires=TYPE(dict)))
    if form.accepts(request,session):
        res = actions.submit_task(request.vars.task,*form.vars.args,**form.vars.vars)
        print res
        session.flash = 'task submitted'
        redirect(URL('view_task',args=res['task_id']))
    return dict(form=form)

def registered_tasks():
    response.headers['Content-Type'] = "application/json"
    return json(actions.registered_tasks())

def task_status():
    """Returns task status and result in JSON format."""
    task_id = request.args(0)
    response.headers['Content-Type'] = "application/json"
    return json(actions.task_status(task_id))

def delete_task():
    task_id = request.args(0)
    print db(pc.taskmeta.task_id==task_id).delete()
    return 

def revoke_task():
    task_id = request.args(0)
    return str(actions.revoke_task(task_id))

def terminate_task():
    task_id = request.args(0)
    return str(actions.terminate_task(task_id))

def kill_task():
    task_id = request.args(0)
    return str(actions.kill_task(task_id))

def view_task():
    task_id = request.args(0)
    return dict(task=actions.task_status(task_id))

def task_monitor():
    page = int(request.vars.page or 0)
    tasks = db(pc.taskmeta).select(
        orderby=~pc.taskmeta.date_done,
        limitby=(100*page, 100*(page+1)))    
    return dict(tasks=tasks,page=page)

def view_taskstate():
    task_id = request.args(0)
    task = pc.taskstate(task_id=task_id)
    return dict(task=task)

def taskstate_monitor():
    page = int(request.vars.page or 0)
    tasks = db(pc.taskstate).select(
        orderby=~pc.taskstate.tstamp,
        limitby=(100*page, 100*(page+1)))
    return dict(tasks=tasks,page=page)

def workers_monitor():
    #return dict(workers=actions.list_workers())
    workers = db(pc.workerstate).select(
        orderby=~pc.workerstate.last_heartbeat)
    return dict(workers=workers)

def inspect_worker():
    return dict(info=actions.inspect_workers([request.args(0)]))

def shutdown_worker():
    return str(actions.shutdown_workers([request.args(0)]))

def edit_periodictask():
    id = request.args(0)
    pc.periodictask.task.requires=IS_IN_SET(TASKS)
    pc.periodictask.args.requires=TYPE(list,parse=False)
    pc.periodictask.kwargs.requires=TYPE(dict,parse=False)
    form = SQLFORM(pc.periodictask,id)
    if form.accepts(request,session):
        session.flash = 'task updated'
        redirect('periodictask_monitor')
    return dict(form=form)

def periodictask_monitor():
    page = int(request.vars.page or 0)
    pc.periodictask.id.represent=lambda id: \
        SPAN(id,' ',
             A('edit',_href=URL('edit_periodictask',args=id)),' ',
             A('delete',callback=URL('delete_periodictask',args=id),delete='tr'))
    pc.periodictask.enabled.represent=lambda e,row: \
        SPAN(SPAN(e,_id='s%s'%row.id),' ',
                  A('on',callback=URL('enable_callback',args=(row.id,'True')),
                    target='s%s'%row.id),'/',
                  A('off',callback=URL('enable_callback',args=(row.id,'False')),
                    target='s%s'%row.id))
    tasks = db(pc.periodictask).select(limitby=(100*page, 100*(page+1)))
    return dict(tasks=tasks,page=page)

def enable_callback():
    id = request.args(0)
    enabled = request.args(1) == 'True'
    db(pc.periodictask.id==id).update(enabled=enabled)
    return request.args(1)

def delete_periodictask():
    id = request.args(0)
    db(pc.periodictask.id==id).delete()
    return 'true'

def last_update():
    row = db(pc.periodictasks).select().first()
    return row and row.last_update.isoformat() or 'unkown'

def manage_intervals():
    table = pc.intervalschedule
    table.id.represent=lambda id: SPAN(id,' [',A('edit',_href=URL(args=id)),']')
    form = SQLFORM(table,request.args(0))
    if form.accepts(request,session): response.flash='saved'
    rows = SQLTABLE(db(table).select(),headers='fieldname:capitalize')
    return locals()

def manage_crontab():
    table = pc.crontab
    table.id.represent=lambda id: SPAN(id,' [',A('edit',_href=URL(args=id)),']')
    form = SQLFORM(table,request.args(0))
    if form.accepts(request,session): response.flash='saved'
    rows = SQLTABLE(db(table).select(),headers='fieldname:capitalize')
    return locals()
