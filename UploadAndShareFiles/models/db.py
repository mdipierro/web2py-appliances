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

mail.settings.server = 'localhost'
mail.settings.sender = 'mdipierro@cs.depaul.edu'
auth.settings.hmac_key = '<your secret key>'   # before define_tables()

auth.define_tables()                           # creates all needed tables
auth.settings.mailer = mail                    # for user email verification
auth.settings.registration_requires_verification = False
auth.settings.registration_requires_approval = False
auth.messages.verify_email = 'Click on the link http://'+request.env.http_host+URL(r=request,c='default',f='user',args=['verify_email'])+'/%(key)s to verify your email'
auth.settings.reset_password_requires_verification = True
auth.messages.reset_password = 'Click on the link http://'+request.env.http_host+URL(r=request,c='default',f='user',args=['reset_password'])+'/%(key)s to reset your password'

production = True #str(request.env.host_name).endswith('web2py.com')
if production:
    hostname='web2py.com'
else:
    hostname='127.0.0.1:8000'

db.define_table('item',
                Field('title',notnull=True),
                Field('file','upload'),
                Field('posted_by',db.auth_user,default=auth.user_id,
                      readable=False,writable=False),
                Field('posted_on','datetime',default=request.now,
                      readable=False,writable=False))
