# -*- coding: utf-8 -*-
#########################################################################
## This scaffolding model makes your app work on Google App Engine too
#########################################################################

response.title='Terremoto Abruzzo'
response.subtitle='Cerca cose, persone e animali'
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
mail.settings.server='localhost:25'
mail.settings.sender='terremoto@mdp.cti.depaul.edu'
mail.settings.login=None
auth=Auth(globals(),db)                      # authentication/authorization
auth.settings.mailer=mail                    # for user email verification
auth.define_tables()                         # creates all needed tables
crud=Crud(globals(),db)                      # for CRUD helpers using auth
#crud.settings.auth=auth                      # (optional) enforces authorization on crud

auth.messages.verify_email = \
    """Clicca qui per verificare il tuo email
      http://mdp.cti.depaul.edu/terremoto/default/user/verify_email/%(key)s
    """
auth.messages.verify_email_subject = 'Terremoto Lost/Found Have/Need'


user_id=auth.user.id if auth.user else None
item_id=request.args[0] if request.args else None

db.define_table('item',
   Field('posted_by',db.auth_user,default=user_id,writable=False,readable=False),
   Field('posted_on','datetime',default=request.now,writable=False),
   Field('category',writable=False,readable=False),
   Field('latitude','double',writable=False,readable=False),
   Field('longitude','double',writable=False,readable=False),
   Field('xwhat',length=128,label='Cosa'),
   Field('xwhere',length=128,label='Dove'),
   Field('xwhen','datetime',default=request.now,label='Quando'),
   Field('image','upload',label='Foto'),
   Field('description','text',label='Descrizione'),
   Field('phone',length=128,label='Contatto Telefonico'),
   Field('email',length=128,label='Contatto Email'))

tr=dict(lost='perso',found='trovato',need='bisogno',have='disponibile')

ne='scrivi qualcosa'
db.item.xwhat.requires=[IS_LENGTH(128),IS_NOT_EMPTY(error_message=ne)]
db.item.xwhere.requires=[IS_LENGTH(128),IS_NOT_EMPTY(error_message=ne)]
db.item.description.requires=[IS_NOT_EMPTY(error_message=ne)]
db.item.email.requires=IS_NULL_OR(IS_EMAIL(error_message='Invalido'))

#########################################################################
## then, to expose authentication
## http://..../[app]/default/user/login
## http://..../[app]/default/user/logout
## http://..../[app]/default/user/register
## http://..../[app]/default/user/profile
## http://..../[app]/default/user/retrieve_password
## http://..../[app]/default/user/change_password
## use the following action in controller default.py
##
##     def user(): return dict(form=auth())
##
## read docs for howto create roles/groups, assign memberships and permissions
##
## to expose CRUD
## http://..../[app]/default/data/tables
## http://..../[app]/default/data/select/[table]
## http://..../[app]/default/data/create/[table]
## http://..../[app]/default/data/read/[table]/[id]
## http://..../[app]/default/data/update/[table]/[id]
## http://..../[app]/default/data/delete/[table]/[id]
## use the following action in controller default.py
##
##     def data(): return dict(form=crud())
##
## to allow automatic download of all uploaded files and enforce authorization
## use the following action in controller default.py
##
##     def download(): return response.download(request,db)
