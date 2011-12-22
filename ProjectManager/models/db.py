# -*- coding: utf-8 -*-

#########################################################################
## This scaffolding model makes your app work on Google App Engine too
## File is released under public domain and you can use without limitations
#########################################################################

if not request.env.web2py_runtime_gae:     
    ## if NOT running on Google App Engine use SQLite or other DB
    db = DAL('sqlite://storage.sqlite') 
else:
    ## connect to Google BigTable (optional 'google:datastore://namespace')
    db = DAL('google:datastore') 
    ## store sessions and tickets there
    session.connect(request, response, db = db) 
    ## or store session in Memcache, Redis, etc.
    ## from gluon.contrib.memdb import MEMDB
    ## from google.appengine.api.memcache import Client
    ## session.connect(request, response, db = MEMDB(Client()))

## by default give a view/generic.extension to all actions from localhost
## none otherwise. a pattern can be 'controller/function.extension'
response.generic_patterns = ['*'] if request.is_local else []

#########################################################################
## Here is sample code if you need for
## - email capabilities
## - authentication (registration, login, logout, ... )
## - authorization (role based authorization)
## - services (xml, csv, json, xmlrpc, jsonrpc, amf, rss)
## - old style crud actions
## (more options discussed in gluon/tools.py)
#########################################################################

from gluon.tools import Auth, Crud, Service, PluginManager, prettydate
auth = Auth(db, hmac_key=Auth.get_or_create_key()) 
crud, service, plugins = Crud(db), Service(), PluginManager()

## create all tables needed by auth if not custom tables
auth.define_tables() 

## configure email
mail=auth.settings.mailer
mail.settings.server = 'logging' or 'smtp.gmail.com:587'
mail.settings.sender = 'you@gmail.com'
mail.settings.login = 'username:password'

## configure auth policy
auth.settings.registration_requires_verification = False
auth.settings.registration_requires_approval = False
auth.settings.reset_password_requires_verification = True

## if you need to use OpenID, Facebook, MySpace, Twitter, Linkedin, etc.
## register with janrain.com, write your domain:api_key in private/janrain.key
from gluon.contrib.login_methods.rpx_account import use_janrain
use_janrain(auth,filename='private/janrain.key')

#########################################################################
## Define your tables below (or better in another model file) for example
##
## >>> db.define_table('mytable',Field('myfield','string'))
##
## Fields can be 'string','text','password','integer','double','boolean'
##       'date','time','datetime','blob','upload', 'reference TABLENAME'
## There is an implicit 'id integer autoincrement' field
## Consult manual for more options, validators, etc.
##
## More API examples for controllers:
##
## >>> db.mytable.insert(myfield='value')
## >>> rows=db(db.mytable.myfield=='value').select(db.mytable.ALL)
## >>> for row in rows: print row.id, row.myfield
#########################################################################




db.define_table('client',
	Field('name'),
	Field('company'),
	Field('email'),
	Field('phone'),
	Field('info', 'text'))
	
db.define_table('department',
	Field('name'),
	Field('location'),
	Field('phone'))
	
db.define_table('employee',
	Field('name', 'reference auth_user'),
	Field('department', 'reference department'),
	Field('position'),
	Field('email'),
	Field('phone'))	
	
db.define_table('project',
    Field('name'),
    Field('client', 'reference client'),
    Field('team', 'list:reference auth_user'),
    Field('description', 'text'),
    Field('due_date', 'date'),
    Field('completed', 'boolean'),
    auth.signature,
    format='%(name)s')	
    
db.define_table('post',
    Field('page_id', 'reference project'),
    Field('post', 'text'),
    Field('created_on', 'datetime', default=request.now),
    Field('created_by', db.auth_user, default=auth.user_id))
    
db.post.post.requires = IS_NOT_EMPTY()
db.post.page_id.readable = db.post.page_id.writable = False
db.post.created_by.readable = db.post.created_by.writable = False
db.post.created_on.readable = db.post.created_on.writable = False

db.define_table('assest',
    Field('page_id', 'reference project'),
    Field('name'),
    Field('assest', 'upload'),
    Field('created_on', 'datetime', default=request.now),
    Field('created_by', db.auth_user, default=auth.user_id))

db.post.post.requires = IS_NOT_EMPTY()    
db.assest.page_id.readable = db.assest.page_id.writable = False
db.assest.created_by.readable = db.assest.created_by.writable = False
db.assest.created_on.readable = db.assest.created_on.writable = False
	