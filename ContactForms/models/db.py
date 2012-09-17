# -*- coding: utf-8 -*-

#########################################################################
## This scaffolding model makes your app work on Google App Engine too
## File is released under public domain and you can use without limitations
#########################################################################

## if SSL/HTTPS is properly configured and you want all HTTP requests to
## be redirected to HTTPS, uncomment the line below:
# request.requires_https()

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
## (optional) optimize handling of static files
# response.optimize_css = 'concat,minify,inline'
# response.optimize_js = 'concat,minify,inline'

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
auth = Auth(db)
crud, service, plugins = Crud(db), Service(), PluginManager()

## create all tables needed by auth if not custom tables
auth.define_tables(username=False, signature=False)

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

## after defining tables, uncomment below to enable auditing
# auth.enable_record_versioning(db)

# arranged in order form simplest to most complex
# todo: think about captcha
# think about widgets ala http://www.web2py.com/AlterEgo/default/show/170
#    http://www.web2pyslices.com/slice/show/1411/widgets-widgets-widgets
#    FormWidget    field_widget
#    http://web2py.com/examples/static/epydoc/web2py.gluon.sqlhtml.FormWidget-class.html
#    google: web2py field widget
# https://snipt.net/rochacbruno/custom-validator-for-web2py-forms/
states = [
    ('AK', 'Alaska'),
    ('AL', 'Alabama'),
    ('AZ', 'Arizona'),
    ('AR', 'Arkansas'),
    ('CA', 'California'),
    ('CO', 'Colorado'),
    ('CT', 'Connecticut'),
    ('DE', 'Delaware'),
    ('FL', 'Florida'),
    ('GA', 'Georgia'),
    ('HI', 'Hawaii'),
    ('ID', 'Idaho'),
    ('IL', 'Illinois'),
    ('IN', 'Indiana'),
    ('IA', 'Iowa'),
    ('KS', 'Kansas'),
    ('KY', 'Kentucky'),
    ('LA', 'Louisiana'),
    ('ME', 'Maine'),
    ('MD', 'Maryland'),
    ('MA', 'Massachusetts'),
    ('MI', 'Michigan'),
    ('MN', 'Minnesota'),
    ('MS', 'Mississippi'),
    ('MO', 'Missouri'),
    ('MT', 'Montana'),
    ('NE', 'Nebraska'),
    ('NV', 'Nevada'),
    ('NH', 'New Hampshire'),
    ('NJ', 'New Jersey'),
    ('NM', 'New Mexico'),
    ('NY', 'New York'),
    ('NC', 'North Carolina'),
    ('ND', 'North Dakota'),
    ('OH', 'Ohio'),
    ('OK', 'Oklahoma'),
    ('OR', 'Oregon'),
    ('PA', 'Pennsylvania'),
    ('RI', 'Rhode Island'),
    ('SC', 'South Carolina'),
    ('SD', 'South Dakota'),
    ('TN', 'Tennessee'),
    ('TX', 'Texas'),
    ('UT', 'Utah'),
    ('VT', 'Vermont'),
    ('VA', 'Virginia'),
    ('WA', 'Washington'),
    ('DC', 'Washington D.C.'),
    ('WV', 'West Virginia'),
    ('WI', 'Wisconsin'),
    ('WY', 'Wyoming')
]
# contact_us
db.define_table(
    't_contactus00',
    Field('name', requires=IS_NOT_EMPTY() ),
    Field('email', requires=IS_EMAIL() ),
	Field('message', 'text', requires=IS_NOT_EMPTY() ),
    )
db.define_table(
    't_contactus01',
    Field('first_name', requires=IS_NOT_EMPTY() ),
    Field('last_name', requires=IS_NOT_EMPTY() ),
    Field('email', requires=IS_EMAIL() ),
	Field('message', 'text', requires=IS_NOT_EMPTY() ),
    )
db.define_table(
    't_contactus02',
    Field('first_name', requires=IS_NOT_EMPTY() ),
    Field('last_name', requires=IS_NOT_EMPTY() ),
    Field('phone', requires=IS_MATCH('^\d{3}-\d{3}-\d{4}$',error_message='Enter a phone number like this: 555-555-1212') ),
    Field('email', requires=IS_EMAIL() ),
	Field('message', 'text', requires=IS_NOT_EMPTY() ),
    )
db.define_table(
    't_contactus03',
    Field('first_name', requires=IS_NOT_EMPTY() ),
    Field('last_name', requires=IS_NOT_EMPTY() ),
    Field('phone', requires=IS_MATCH('^\d{3}-\d{3}-\d{4}$',error_message='Enter a phone number like this: 555-555-1212') ),
    Field('email', requires=IS_EMAIL()),
	Field('contact_preference', default='email', requires=IS_IN_SET(['phone','email'])),
	Field('message', 'text', requires=IS_NOT_EMPTY() ),	
    )
db.define_table(
    't_contactus04',
    Field('first_name', requires=IS_NOT_EMPTY() ),
    Field('last_name', requires=IS_NOT_EMPTY() ),
    Field('phone', requires=IS_MATCH('^\d{3}-\d{3}-\d{4}$',error_message='Enter a phone number like this: 555-555-1212') ),
    Field('email', requires=IS_EMAIL()),
	Field('contact_preference', default='email', requires=IS_IN_SET(['phone','email'])),
    Field('age', requires=(IS_NOT_EMPTY(), IS_INT_IN_RANGE(0, 200)) ),
    Field('profession', requires=IS_NOT_EMPTY() ),
	Field('previously_registered', default='no', requires=IS_IN_SET(['yes','no'])),
	Field('previous_email', required=False),	
	Field('message', 'text', requires=IS_NOT_EMPTY() ),	
    )

# sign_up
db.define_table(
    't_signup00',
    Field('first_name', requires=IS_NOT_EMPTY() ),
    Field('last_name', requires=IS_NOT_EMPTY() ),
    Field('street_address1', requires=IS_NOT_EMPTY() ),
    Field('street_address2'),
    Field('city'),
    Field('state', requires=IS_IN_SET(states)),
    Field('zip', requires=IS_MATCH('^\d{5}$',error_message='enter a valid 5 digit zipcode') ),	
    Field('phone', requires=IS_MATCH('^\d{3}-\d{3}-\d{4}$',error_message='Enter a phone number like this: 555-555-1212') ),
    )
db.define_table(
    't_signup01',
    Field('first_name', requires=IS_NOT_EMPTY() ),
    Field('last_name', requires=IS_NOT_EMPTY() ),
    Field('street_address1'),
    Field('street_address2'),
    Field('city'),
    Field('state', requires=IS_IN_SET(states)),
    Field('zip', requires=IS_MATCH('^\d{5}$',error_message='enter a valid 5 digit zipcode') ),	
    Field('email', requires=IS_EMAIL()),
    )
db.define_table(
    't_signup02',
    Field('first_name', requires=IS_NOT_EMPTY() ),
    Field('last_name', requires=IS_NOT_EMPTY() ),
    Field('street_address1'),
    Field('street_address2'),
    Field('city'),
    Field('state', requires=IS_IN_SET(states)),
    Field('zip', requires=IS_MATCH('^\d{5}$',error_message='enter a valid 5 digit zipcode') ),	
    Field('phone', requires=IS_MATCH('^\d{3}-\d{3}-\d{4}$',error_message='Enter a phone number like this: 555-555-1212') ),
    Field('email', requires=IS_EMAIL()),
    )

db.define_table(
    't_signup03',
    Field('first_name', requires=IS_NOT_EMPTY() ),
    Field('last_name', requires=IS_NOT_EMPTY() ),
    Field('street_address1'),
    Field('street_address2'),
    Field('city'),
    Field('state', requires=IS_IN_SET(states)),
    Field('zip', requires=IS_MATCH('^\d{5}$',error_message='enter a valid 5 digit zipcode') ),	
    Field('phone', requires=IS_MATCH('^\d{3}-\d{3}-\d{4}$',error_message='Enter a phone number like this: 555-555-1212') ),
    Field('email', requires=IS_EMAIL()),
	Field('contact_preference', default='email', requires=IS_IN_SET(['phone','email'])),
    )
db.define_table(
    't_signup04',
    Field('first_name', requires=IS_NOT_EMPTY() ),
    Field('last_name', requires=IS_NOT_EMPTY() ),
    Field('street_address1'),
    Field('street_address2'),
    Field('city'),
    Field('state', requires=IS_IN_SET(states)),
    Field('zip', requires=IS_MATCH('^\d{5}$',error_message='enter a valid 5 digit zipcode') ),	
    Field('phone', requires=IS_MATCH('^\d{3}-\d{3}-\d{4}$',error_message='Enter a phone number like this: 555-555-1212') ),
    Field('email', requires=IS_EMAIL()),
	Field('contact_preference', default='email', requires=IS_IN_SET(['phone','email'])),
    Field('date_of_birth', requires=IS_DATE()),
    Field('profession'),
    )

# appointment
db.define_table(
    't_appointment00',
    Field('name', requires=IS_NOT_EMPTY() ),
    Field('phone', requires=IS_MATCH('^\d{3}-\d{3}-\d{4}$',error_message='Enter a phone number like this: 555-555-1212') ),
    Field('appointment', 'date', comment='Click in box to activate date picker.', requires=IS_DATE() ),
    )

db.define_table(
    't_appointment01',
    Field('name', requires=IS_NOT_EMPTY() ),
    Field('phone', requires=IS_MATCH('^\d{3}-\d{3}-\d{4}$',error_message='Enter a phone number like this: 555-555-1212') ),
    Field('monday', 'boolean'),
    Field('tuesday', 'boolean'),
    Field('wednesday', 'boolean'),
    Field('thursday', 'boolean'),
    Field('friday', 'boolean'),
    )
db.define_table(
    't_appointment02',
    Field('name', requires=IS_NOT_EMPTY() ),
    Field('phone', requires=IS_MATCH('^\d{3}-\d{3}-\d{4}$',error_message='Enter a phone number like this: 555-555-1212') ),
    Field('monday_am', 'boolean'),
    Field('monday_pm', 'boolean'),
    Field('tuesday_am', 'boolean'),
    Field('tuesday_pm', 'boolean'),
    Field('wednesday_am', 'boolean'),
    Field('wednesday_pm', 'boolean'),
    Field('thursday_am', 'boolean'),
    Field('thursday_pm', 'boolean'),
    Field('friday_am', 'boolean'),
    Field('friday_pm', 'boolean'),	
    )

db.define_table(
    't_appointment03',
    Field('name', requires=IS_NOT_EMPTY() ),
    Field('phone', requires=IS_MATCH('^\d{3}-\d{3}-\d{4}$',error_message='Enter a phone number like this: 555-555-1212') ),
    Field('from_date', 'datetime', requires=IS_DATETIME() ),
    Field('to_date', 'datetime', requires=IS_DATETIME() ),
    )
	


	
	