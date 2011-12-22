# -*- coding: utf-8 -*- 

#########################################################################
## This scaffolding model makes your app work on Google App Engine too
#########################################################################

if request.env.web2py_runtime_gae:            # if running on Google App Engine
    db = DAL('gae')                           # connect to Google BigTable
    session.connect(request, response, db = db) # and store sessions and tickets there
else:                                         # else use a normal relational database
    db = DAL('sqlite://storage.sqlite')       # if not, use SQLite or other DB


#########################################################################
## Here is sample code if you need for 
## - email capabilities
## - authentication (registration, login, logout, ... )
## - authorization (role based authorization)
## - services (xml, csv, json, xmlrpc, jsonrpc, amf, rss)
## - crud actions
## (more options discussed in gluon/tools.py)
#########################################################################

from gluon.tools import *
mail = Mail()                                  # mailer
auth = Auth(globals(),db)                      # authentication/authorization
crud = Crud(globals(),db)                      # for CRUD helpers using auth
service = Service(globals())                   # for json, xml, jsonrpc, xmlrpc, amfrpc
plugins = PluginManager()
plugins.wiki.widgets=settings.widgets

mail.settings.server = settings.production and settings.email_server or 'logging'
mail.settings.sender = settings.email_sender or 'you@example.com'
mail.settings.login = settings.email_password

auth.settings.hmac_key = '<your secret key>'   # before define_tables()

db.define_table(
    'auth_user',
    Field('username',length=512,writable=False),
    Field('first_name', length=128, default=''),
    Field('last_name', length=128, default=''),
    Field('email', length=128, default='', unique=True),
    Field('password', 'password', length=512,
          readable=False, label='Password'),
    Field('background',
          writable=False, readable=False, default=''),
    Field('registration_key', length=512,
          writable=False, readable=False, default=''),
    Field('reset_password_key', length=512,
          writable=False, readable=False, default=''),
    Field('registration_id', length=512,
          writable=False, readable=False, default=''),
    format='%(first_name)s %(last_name)s')

db.auth_user.username.requires=IS_NOT_IN_DB(db,'auth_user.username')
db.auth_user.first_name.requires = \
  IS_NOT_EMPTY(error_message=auth.messages.is_empty)
db.auth_user.last_name.requires = \
  IS_NOT_EMPTY(error_message=auth.messages.is_empty)
db.auth_user.password.requires = [CRYPT(key=auth.settings.hmac_key)]
db.auth_user.email.requires = [
  IS_EMAIL(error_message=auth.messages.invalid_email),
  IS_NOT_IN_DB(db, db.auth_user.email)]

auth.define_tables()

auth.settings.mailer = mail                    # for user email verification
auth.settings.registration_requires_verification = False
auth.settings.registration_requires_approval = False
auth.messages.verify_email = 'Click on the link http://'+request.env.http_host+URL(r=request,c='default',f='user',args=['verify_email'])+'/%(key)s to verify your email'
auth.settings.reset_password_requires_verification = True
auth.messages.reset_password = 'Click on the link http://'+request.env.http_host+URL(r=request,c='default',f='user',args=['reset_password'])+'/%(key)s to reset your password'


db.define_table('enrollment',
                Field('user_id',db.auth_user,default=auth.user_id),
                Field('org_unit_code'),
                Field('org_unit_name'),
                Field('role_code'),
                Field('org_defined_id')) # reference to auth_user.registration_id
                
D2LKEYS=('first_name',
         'last_name',
         'org_defined_id',
         'role_code',
         'org_unit_code',
         'org_unit_name')

def handle_d2l_call():
    if not session.d2l: session.d2l={}
    for key in D2LKEYS:
        if not key in request.vars: 
            break
        else:
            session.d2l[key]=request.vars[key]
    if len(session.d2l)==len(D2LKEYS) and auth.user:
        if not session.d2l['org_defined_id']==auth.user.registration_id:            
            raise HTTP(404)
        db(db.auth_user.id==auth.user.id).update(first_name=session.d2l['first_name'],
                                                 last_name=session.d2l['last_name'])
        auth.user.first_name=session.d2l['first_name']
        auth.user.last_name=session.d2l['last_name']
        db(db.enrollment.org_unit_code==session.d2l['org_unit_code'])\
            (db.enrollment.org_defined_id==session.d2l['org_defined_id']).delete()
        db.enrollment.insert(
            org_defined_id = session.d2l['org_defined_id'],
            role_code=session.d2l['role_code'],
            org_unit_code=session.d2l['org_unit_code'],
            org_unit_name=session.d2l['org_unit_name'])
        del session.d2l['first_name']
handle_d2l_call()

# make sure if you have a failed attempt to visit a page you get there!

if auth.user and session.target:
    url=session.target
    session.target=None
    redirect(url)

