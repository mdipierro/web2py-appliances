is_phone = IS_MATCH('^(\+\d{2}\-)?[\d\-]*(\#\d+)?$')

TASK_TYPES = ('Phone', 'Fax', 'Mail', 'Meet')

if auth.is_logged_in():
   me=auth.user.id
else:
   me=None

db.define_table('company',
    Field('name'),
    Field('url'),
    Field('address'),
    Field('phone'),
    Field('fax'),
    Field('created_by',db.auth_user,default=me,writable=False,readable=False),
    Field('created_on','datetime',default=request.now,writable=False,readable=False))

db.company.name.requires=[IS_NOT_EMPTY(),IS_NOT_IN_DB(db,'company.name')]
db.company.url.requires=IS_EMPTY_OR(IS_URL())
db.company.phone.requires=is_phone
db.company.fax.requires=is_phone

db.define_table('person',
    Field('name'),
    Field('company',db.company),
    Field('role'),
    Field('address'),
    Field('phone'),
    Field('fax'),
    Field('created_by',db.auth_user,default=me,writable=False,readable=False),
    Field('created_on','datetime',default=request.now,writable=False,readable=False))


db.person.name.requires=[IS_NOT_EMPTY(),IS_NOT_IN_DB(db,'person.name')]
db.person.company.requires=IS_IN_DB(db,'company.id','%(name)s')
db.person.phone.requires=is_phone
db.person.fax.requires=is_phone

db.define_table('task',
    Field('title'),
    Field('task_type'),
    Field('person',db.person,default=None),
    Field('description','text'),
    Field('start_time','datetime'),
    Field('stop_time','datetime'),
    Field('created_by',db.auth_user,default=me,writable=False,readable=False),
    Field('created_on','datetime',default=request.now,writable=False,readable=False))

db.task.title.requires=IS_NOT_EMPTY()
db.task.task_type.requires=IS_IN_SET(TASK_TYPES)
db.task.person.requires=IS_IN_DB(db,'person.id','%(name)s')
db.task.start_time.default=request.now
db.task.stop_time.default=request.now

db.define_table('log',
    Field('person',db.person),
    Field('body','text'),
    Field('created_by',db.auth_user,default=me,writable=False,readable=False),
    Field('created_on','datetime',default=request.now,writable=False,readable=False))

db.log.person.requires=IS_IN_DB(db,'person.id','%(name)s')
db.log.body.requires=IS_NOT_EMPTY()

db.define_table('document',
    Field('person',db.person),
    Field('name'),
    Field('file','upload'),
    Field('created_by',db.auth_user,default=me,writable=False,readable=False),
    Field('created_on','datetime',default=request.now,writable=False,readable=False))

db.document.person.requires=IS_IN_DB(db,'person.id','%(name)s')
db.document.name.requires=IS_NOT_EMPTY()
db.document.file.requires=IS_NOT_EMPTY()
