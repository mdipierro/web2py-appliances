# -*- coding: utf-8 -*-
if request.env.web2py_runtime_gae:            # if running on Google App Engine
    db = DAL('gae')                           # connect to Google BigTable
    session.connect(request, response, db = db) # and store sessions and tickets there
else:                                         # else use a normal relational database
    db = DAL('sqlite://storage.sqlite')       # if not, use SQLite or other DB

from gluon.tools import *
mail = Mail()                                  # mailer
auth = Auth(globals(),db)                      # authentication/authorization
crud = Crud(globals(),db)                      # for CRUD helpers using auth
service = Service(globals())                   # for json, xml, jsonrpc, xmlrpc, amfrpc

mail.settings.server = 'logging' if not settings.production else settings.email_server
mail.settings.sender = settings.email_sender
mail.settings.login = settings.email_login

auth.settings.hmac_key = settings.hmac_key

db.define_table('auth_user',
                Field('first_name', length=512,default=''),
                Field('last_name', length=512,default=''),
                Field('email', length=512,default='',requires=(IS_EMAIL(),IS_NOT_IN_DB(db,'auth_user.email'))),
                Field('password', 'password', readable=False, label='Password', requires=[CRYPT(auth.settings.hmac_key)]),
                Field('sex',requires=IS_IN_SET(('male','female','other'))),
                Field('birth_place'),
                Field('birth_date','date'),
                Field('patient','boolean',default=True),
                Field('doctor','boolean',default=False),
                Field('nurse','boolean',default=False),
                Field('administrator','boolean',default=False),
                Field('trusted_doctors'),
                Field('trusted_others'),
                Field('registration_key', length=512,writable=False, readable=False,default=''),
                Field('registration_id', length=512,writable=False, readable=False,default=''),
                Field('reset_password_key', length=512,writable=False, readable=False, default='',
                      label=auth.messages.label_reset_password_key),
                format='%(first_name)s %(last_name)s',
                )

db.auth_user.birth_date.requires=IS_NOT_IN_DB(db((db.auth_user.first_name==request.vars.first_name)&
                                                 (db.auth_user.last_name==request.vars.last_name)),
                                              'auth_user.birth_date')

doctors = db.auth_user.doctor==True
nurses = db.auth_user.nurse==True
administrators = db.auth_user.administrator==True
db.auth_user.trusted_doctors.requires=IS_IN_DB(db(doctors),
                                               'auth_user.id',
                                               'Dr %(first_name)s %(last_name)s',
                                               multiple=True)

db.auth_user.trusted_others.requires=IS_IN_DB(db(nurses|administrators|doctors),
                                              'auth_user.id',
                                              '%(first_name)s %(last_name)s',
                                              multiple=True)

auth.define_tables()                           # creates all needed tables
auth.settings.mailer = mail                    # for user email verification
auth.settings.registration_requires_verification = False
auth.settings.registration_requires_approval = False
auth.messages.verify_email = 'Click on the link http://'+request.env.http_host+URL(r=request,c='default',f='user',args=['verify_email'])+'/%(key)s to verify your email'
auth.settings.reset_password_requires_verification = True
auth.messages.reset_password = 'Click on the link http://'+request.env.http_host+URL(r=request,c='default',f='user',args=['reset_password'])+'/%(key)s to reset your password'
