# -*- coding: utf-8 -*-
#########################################################################
## This scaffolding model makes your app work on Google App Engine too
#########################################################################

response.title='Need-A-Ride'
response.subtitle='to the Muon Collider Physics Workshop'
GOOGLEMAP_KEY="ABQIAAAAT5em2PdsvF3z5onQpCqv0RRbmBRVqcetsYYPAZkdVkJ1U_-f7hQyRsL4C5GpXpg29_Qza9VuE2zX2w"

try:
    from gluon.contrib.gql import *  # if running on Google App Engine
except:
    db = DAL('sqlite://storage.db')  # if not, use SQLite or other DB
else:
    db = GQLDB()  # connect to Google BigTable
    session.connect(request, response, db=db)  # and store sessions there
    # or use the following lines to store sessions in Memcache
    #from gluon.contrib.memdb import MEMDB
    #from google.appengine.api.memcache import Client
    #session.connect(request, response, db=MEMDB(Client()))

#########################################################################
## uncomment the following line if you do not want sessions
#session.forget()
#########################################################################

#########################################################################
## Define your tables below, for example
##
## >>> db.define_table('mytable',Field('myfield','string'))
##
## Fields can be 'string','text','password','integer','double','booelan'
##       'date','time','datetime','blob','upload', 'reference TABLENAME'
## There is an implicit 'id integer autoincrement' field
## Consult manual for more options, validators, etc.
##
## More API examples for controllers:
##
## >>> db.mytable.insert(myfield='value')
## >>> rows=db(db.mytbale.myfield=='value).select(db.mytable.ALL)
## >>> for row in rows: print row.id, row.myfield
#########################################################################

#########################################################################
## Here is sample code if you need:
## - email capabilities
## - authentication (registration, login, logout, ... )
## - authorization (role based authorization)
## - crud actions
## uncomment as needed
#########################################################################

from gluon.tools import *
mail=Mail()                                  # mailer
mail.settings.server = 'localhost:25'
mail.settings.sender = 'eichten@mac.com'
mail.settings.login=None
auth=Auth(globals(),db)            # authentication/authorization
auth.settings.mailer=mail          # for user email verification
auth.define_tables()               # creates all needed tables
crud=Crud(globals(),db)            # for CRUD helpers using auth
#crud.settings.auth=auth           # (optional) enforces authorization on crud

auth.messages.verify_email = \
    """Click here to verify your email:
      http://web2py.com/needaride/default/user/verify_email/%(key)s
    """
auth.messages.verify_email_subject = 'Need-A-Ride'
auth.settings.registration_requires_verification = True

user_id=auth.user.id if auth.user else None
item_id=request.args[0] if request.args else None

HOTELS="""Aurora Fox Valley Inn (aurora)
Extended Stay America (Warrenville)
Red Roof Inn (Naperville)
Homestead Village (Naperville)
Best Western (Naperville)
Comfort Inn (Geneva)
Candlewood Suites (Warrenville)
Holidey Inn (Lisle)
Hilton Garden (Warrenville)
Hilton Inn (Lisle)
Pheasant Run Resort (St Charles)
Mariott Springhill (Warrenville)
Residence Inn (Warrenville)
Fairfield Inn (Naperville)
Towneplace Suites""".split('\n')
HOTELS.sort()
HOTELS.append("Chicago Downtown")
HOTELS.append("O'Hare Airport")
HOTELS.append("Midway Airport")
HOTELS.append("Other...")

db.define_table('item',
                Field('posted_by',db.auth_user,default=user_id,writable=False,readable=False),
                Field('posted_on','datetime',default=request.now,writable=False),
                Field('name',default=('%(first_name)s %(last_name)s' % auth.user) if auth.user else ''),
                Field('request',label='Ride',requires=IS_IN_SET(('NEED','OFFER'))),
                Field('location',requires=IS_IN_SET(HOTELS)),
                Field('comments','text'),
                Field('email',default=auth.user.email if auth.user else '',writable=False,readable=False))

db.item.email.requires=IS_NULL_OR(IS_EMAIL())
