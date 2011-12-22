from gluon.utils import web2py_uuid

db.define_table('quiz',
                Field('owner',db.auth_user,
                      default=auth.user_id,
                      writable=False),
                Field('code',default=web2py_uuid(),
                      writable=False),
                Field('title'),
                Field('body','text'),
                Field('retake','boolean',default=False),
                Field('time_restricted','boolean',default=False),
                Field('start_time','datetime'),
                Field('stop_time','datetime'),
                Field('duration','integer',comment='seconds',default=180*60))

db.define_table('report',
                Field('student',db.auth_user),
                Field('quiz',db.quiz),
                Field('grade'),
                Field('form'),
                Field('answers','text'),
                Field('start_time','datetime'),
                Field('stop_time','datetime'))
