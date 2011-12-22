#!/usr/bin/python
# -*- coding: utf-8 -*-
# ########################################################################
# # This scaffolding model makes your app work on Google App Engine too
# ########################################################################

try:
    from gluon.contrib.gql import *  # if running on Google App Engine
except:
    db = DAL('sqlite://semacode.db')  # if not, use SQLite or other DB
else:
    db = GQLDB()  # connect to Google BigTable
    session.connect(request, response, db=db)  # and store sessions ther

# ########################################################################
# # uncomment the following line if you do not want sessions
# session.forget()
# ########################################################################

# ########################################################################
# # Define your tables below, for example
##
# # >>> db.define_table('mytable',Field('myfield','string'))
##
# # Fields can be 'string','text','password','integer','double','booelan'
# #       'date','time','datetime','blob','upload', 'reference TABLENAME'
# # There is an implicit 'id integer autoincrement' field
# # Consult manual for more options, validators, etc.
##
# # More API examples for controllers:
##
# # >>> db.mytable.insert(myfield='value')
# # >>> rows=db(db.mytbale.myfield=='value).select(db.mytable.ALL)
# # >>> for row in rows: print row.id, row.myfield
# ########################################################################

# ########################################################################
# # Here is sample code if you need:
# # - email capabilities
# # - authentication (registration, login, logout, ... )
# # - authorization (role based authorization)
# # - crud actions
# # uncomment as needed
# ########################################################################

# from gluon.tools import Mail, Auth, Crud     # new in web2py 1.56
# mail=Mail()                                  # mailer
# mail.settings.server='smtp.gmail.com:587'    # your SMTP server
# mail.settings.sender='you@gmail.com'         # your email
# mail.settings.login='username:password'      # your credentials
# auth=Auth(globals(),db)                      # authentication/authorization
# auth.settings.mailer=mail                     # for user email verification
# auth.define_tables()                         # creates all needed tables
# crud=Crud(globals(),db)                      # for CRUD helpers using auth
# crud.settings.auth=auth          # (optional) enforces authorization on crud

# ########################################################################
# # then, to expose authentication
# # http://..../[app]/default/user/login
# # http://..../[app]/default/user/logout
# # http://..../[app]/default/user/register
# # http://..../[app]/default/user/profile
# # http://..../[app]/default/user/retrieve_password
# # http://..../[app]/default/user/change_password
# # use the following action in controller default.py
##
# #     def user(): return dict(form=auth())
##
# # read docs for howto create roles/groups, assign memberships and permissions
##
# # to expose CRUD
# # http://..../[app]/default/data/tables
# # http://..../[app]/default/data/select/[table]
# # http://..../[app]/default/data/create/[table]
# # http://..../[app]/default/data/read/[table]/[id]
# # http://..../[app]/default/data/update/[table]/[id]
# # http://..../[app]/default/data/delete/[table]/[id]
# # use the following action in controller default.py
##
# #     def data(): return dict(form=crud())
##
# # to allow automatic download of all uploaded files and enforce authorization
# # use the following action in controller default.py
##
# #     def download(): return response.download(request,db)
