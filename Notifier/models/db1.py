# coding: utf8
import datetime
week = datetime.timedelta(days=7)

STATUSES = ('assigned','accepted','rejected','reassigned','completed')

db.define_table('task',
                Field('title',requires=IS_NOT_EMPTY()),
                Field('description','text'),
                Field('assigned_to','reference auth_user'),
                Field('status',requires=IS_IN_SET(STATUSES),
                      default=STATUSES[0]),
                Field('deadline','date',default=request.now+week),
                auth.signature)


auth.enable_record_versioning(db)

db.task.created_on.represent = lambda v,row: prettydate(v)
db.task.deadline.represent = lambda v,row: SPAN(prettydate(v),_class='overdue' if v and v<datetime.date.today() else None)

def fullname(user_id):
    if user_id is None:
        return "Unknown"
    return "%(first_name)s %(last_name)s (id:%(id)s)" % db.auth_user(user_id)

def show_status(status,row=None):
    return SPAN(status,_class=status)

db.task.status.represent = show_status

#db(db.task).delete()
#from gluon.contrib.populate import populate
#populate(db.task,100)

def send_email_realtime(to, subject, message, sender):
    if not isinstance(to,list): to = [to]
    # if auth.user: to = [email for email in to if not to==auth.user.email]    
    mail.settings.sender = sender
    return mail.send(to=to, subject=subject, message=message or '(no message)')


#db.define_table('email',
#                Field('to_addrs','list:string'),
#                Field('subject'),
#                Field('body','text'),
#                Field('sender'),
#                Field('status',requires=IS_IN_SET(('pending','sent','failed'))),
#                Field('queued_datetime','datetime',default=request.now),
#                Field('sent_on','datetime',default=None),
#                )

def send_email_deferred(to, subject, message, sender):
    if not isinstance(to,list): to = [to]
    #db.email.insert(to_addrs=to,subject=subject,body=message,sender=sender,
    #                status='pending')
    #scheduler.queue_task(send_pending_emails)
    scheduler.queue_task(send_email_realtime,
                         pvars=dict(to=to,subject=subject,
                                    message=message,sender=sender))

#def send_pending_emails():
#    rows = db(db.email.status=='pending').select()
#    for row in rows:
#        ret = send_email_realtime(to=row.to_addrs, subject=row.subject,
#                                  message=row.body, sender=row.sender)
#        row.status = 'sent' if ret else 'failed'

def send_email(to, subject, message, sender):
    if EMAIL_POLICY == 'realtime':
        return send_email_realtime(to, subject, message, sender)
    else:
        return send_email_deferred(to, subject, message, sender)


def callback_on_comment(form):
    task_id = db.plugin_comments_post.record_id.default
    task = db.task(task_id)
    me = auth.user.id
    user_id = task.created_by if task.assigned_to==me else task.assigned_to
    send_email(to=db.auth_user(user_id).email,
               sender=auth.user.email,
               subject="New Comment About: %s" % task.title,
               message=form.vars.body)

plugins.comments.callbacks['task'] = callback_on_comment
