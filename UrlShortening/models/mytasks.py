from gluon.scheduler import Scheduler

def emailme():   
    me = 'mdipierro@cs.depaul.edu'
    message = '%s users' % db(db.auth_user).count()
    mailer.send(to=me, subject='stats', message=message)
    return 'done!'

scheduler = Scheduler(db,dict(emailme=emailme))
if db(db.scheduler_task).isempty():
    db.scheduler_task.insert(
        application_name=request.application,
        task_name='email me user count',
        function_name='emailme',args=[],vars={},
        period=3600*24,repeats=0)
