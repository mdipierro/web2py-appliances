# -*- coding: utf-8 -*-

#########################################################################
##Written by C. S. Schroeder, A Theory of Publishing
##Copyright (C) 2011 Equimind Financial LLC.
##
##Permission is hereby granted, free of charge, to any
##person obtaining a copy of this software and associated
##documentation files (the "Software"), to deal in the
##Software without restriction, including without limitation
##the rights to use, copy, modify, merge, publish,
##distribute, sublicense, and/or sell copies of the
##Software, and to permit persons to whom the Software is
##furnished to do so, subject to the following conditions:
##
##The above copyright notice and this permission notice
##shall be included in all copies or substantial portions of
##the Software.
##
##THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY
##KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE
##WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR
##PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS
##OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR
##OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR
##OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE
##SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
##
##  Powered by web2py, Thanks Massimo!
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
T.current_languages = ['en', 'en-en']
#T.force('es-es')
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

if len(db(db.auth_group.role == 'admin').select())<1:
    db.auth_group.insert(role= 'admin', description="For administration of memebers")
if len(db(db.auth_group.role == 'reviewer').select())<1:
    db.auth_group.insert(role= 'reviewer', description="For submitting reviews")

## user must be admin of application
## configure email
mail=auth.settings.mailer
## configure auth policy
auth.settings.registration_requires_verification = False
auth.settings.registration_requires_approval = False
auth.settings.reset_password_requires_verification = True

## if you need to use OpenID, Facebook, MySpace, Twitter, Linkedin, etc.
## register with janrain.com, write your domain:api_key in private/janrain.key
##from gluon.contrib.login_methods.rpx_account import use_janrain
##use_janrain(auth,filename='private/janrain.key')

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


db.define_table('reviewer', 
                Field('screenname', 'string', length=(30,2)),
                Field('userid', db.auth_user),
                Field('photo', 'upload', length=(130000, 1024), requires=[IS_IMAGE(), IS_LENGTH(130000, 1024)]), 
                Field('city', 'string', length=25, requires=IS_LENGTH(25,2)), 
                Field('state', 'string', length=25,requires=IS_LENGTH(25,2)), 
                Field('country', 'string', length=25,requires=IS_LENGTH(25,2)), 
                Field('loves', 'string', length=200,requires=IS_LENGTH(200,2)), 
                Field('likes', 'string', length=200,requires=IS_LENGTH(200,2)), 
                Field('dislikes', 'string', length=200,requires=IS_LENGTH(200,2)), 
                Field('about_me', 'text'))

db.define_table('region', 
                Field('name', 'string', length=25,requires=IS_LENGTH(25,2)),
                Field('blurb', 'string', length=500,requires=IS_LENGTH(500,2)),
                Field('photo', 'upload', length=(130000, 1024), requires=[IS_IMAGE(), IS_LENGTH(130000, 1024)]), 
                Field('city', 'string', length=25, requires=IS_LENGTH(25,2)), 
                Field('state', 'string', length=25,requires=IS_LENGTH(25,2)), 
                Field('country', 'string', length=25,requires=IS_LENGTH(25,2)), 
                Field('product_categories', 'string', length=400,requires=IS_LENGTH(400,2)), 
                Field('product_lines', 'string', length=400,requires=IS_LENGTH(400,2)), 
                Field('famous_for', 'string', length=200,requires=IS_LENGTH(200,2)), 
                Field('about', 'text'))

db.define_table('place', 
                Field('name', 'string', length=25,requires=IS_LENGTH(25,2)), 
                Field('blurb', 'string', length=500, requires=IS_LENGTH(500,2)),
                Field('photo', 'upload', length=(130000, 1024), requires=[IS_IMAGE(), IS_LENGTH(130000, 1024)]), 
                Field('region', db.region, required=True, requires=IS_IN_DB(db, 'region.id', '%(name)s')),
                Field('type', 'string', length=25, requires=IS_IN_SET([T('computing'), T('audio-visual'), T('mobile')])),
                Field('description', 'string', length=400,requires=IS_LENGTH(400,2)),
                Field('cost', 'string', length=200,requires=IS_LENGTH(200,2)), 
                Field('about', 'text'))

db.define_table('event', 
                Field('name', 'string', length=25,requires=IS_LENGTH(25,2)), 
                Field('blurb', 'string', length=500,requires=IS_LENGTH(500,2)),
                Field('photo', 'upload', length=(130000, 1024), requires=[IS_IMAGE(), IS_LENGTH(130000, 1024)]), 
                Field('region', db.region, required=True, requires=IS_IN_DB(db, 'region.id', '%(name)s')),
                Field('place', db.place, requires=IS_NULL_OR(IS_IN_DB(db, 'place.id', '%(name)s'))),
                Field('description', 'string', length=200,requires=IS_LENGTH(200,2)),
                Field('cost', 'string', length=200,requires=IS_LENGTH(200,2)), 
                Field('about', 'text'))


class RatingWidget(SQLFORM.widgets.options):
    @staticmethod
    def widget(field, value, **attributes):
        attr = SQLFORM.widgets.options._attributes(field, {}, **attributes)

        if isinstance(field.requires, IS_NULL_OR)\
             and hasattr(field.requires.other, 'options'):
            opts = [TD(INPUT(_type='radio', _name=field.name,
                             _value='', value=value), '')]
            options = field.requires.other.options()
        elif hasattr(field.requires, 'options'):
            opts = []
            options = field.requires.options()
        else:
            raise SyntaxError, 'widget cannot determine options of %s' % field
        opts += [TD(INPUT(_type='radio', _name=field.name,
                          _value=k, value=value), '') for (k, v) in options]
        return TABLE(TR(*(['low']+opts+['high'])), **attr) 


import datetime

db.define_table('region_review', 
                Field('ref_id', db.region, required=True, requires=IS_IN_DB(db, 'region.id', '%(name)s')),
                Field('blurb', 'string', length=500,requires=IS_LENGTH(500,2)),
                Field('author', db.reviewer, requires=IS_IN_DB(db, 'reviewer.id', "%(screenname)s")),
                Field('photo', 'upload', length=(130000, 1024), requires=[IS_IMAGE(), IS_LENGTH(130000, 1024)]), 
                Field('photo1', 'upload', length=(130000, 1024), requires=[IS_IMAGE(), IS_LENGTH(130000, 1024)]), 
                Field('photo2', 'upload', length=(130000, 1024), requires=[IS_IMAGE(), IS_LENGTH(130000, 1024)]), 
                Field('title', 'string', length=100,requires=IS_LENGTH(100,2)), 
                Field('subject', 'string', length=25,requires=IS_LENGTH(25,2)), 
                Field('the_good', 'string', length=250,requires=IS_LENGTH(250,2)), 
                Field('the_bad', 'string', length=250,requires=IS_LENGTH(250,2)), 
                Field('date', 'datetime', default=datetime.datetime.now()), 
                Field('text', 'text'), 
                Field('rating', 'integer', default=1, requires=IS_IN_SET([1,2,3,4,5]), widget=RatingWidget.widget),
                Field('publish', 'boolean', default=True)
                )

db.define_table('place_review', 
                Field('ref_id', db.place, required=True, requires=IS_IN_DB(db, 'place.id', '%(name)s')),
                Field('blurb', 'string', length=500,requires=IS_LENGTH(500,2)),
                Field('author', db.reviewer, requires=IS_IN_DB(db, 'reviewer.id', "%(screenname)s")),
                Field('photo', 'upload', length=(130000, 1024), requires=[IS_IMAGE(), IS_LENGTH(130000, 1024)]), 
                Field('photo1', 'upload', length=(130000, 1024), requires=[IS_IMAGE(), IS_LENGTH(130000, 1024)]), 
                Field('photo2', 'upload', length=(130000, 1024), requires=[IS_IMAGE(), IS_LENGTH(130000, 1024)]), 
                Field('title', 'string', length=100,requires=IS_LENGTH(100,2)), 
                Field('subject', 'string', length=25,requires=IS_LENGTH(25,2)), 
                Field('the_good', 'string', length=250,requires=IS_LENGTH(250,2)), 
                Field('the_bad', 'string', length=250,requires=IS_LENGTH(250,2)), 
                Field('date', 'datetime', default=datetime.datetime.now()), 
                Field('text', 'text'),
                Field('rating', 'integer', default=1,  requires=IS_IN_SET([1,2,3,4,5]), widget=RatingWidget.widget),
                Field('publish', 'boolean', default=True)
                )

db.define_table('event_review', 
                Field('ref_id', db.event, required=True, requires=IS_IN_DB(db, 'event.id', '%(name)s')),
                Field('blurb', 'string', length=500,requires=IS_LENGTH(500,2)),
                Field('author', db.reviewer, requires=IS_IN_DB(db, 'reviewer.id', "%(screenname)s")),
                Field('photo', 'upload', length=(130000, 1024), requires=[IS_IMAGE(), IS_LENGTH(130000, 1024)]), 
                Field('photo1', 'upload', length=(130000, 1024), requires=[IS_IMAGE(), IS_LENGTH(130000, 1024)]), 
                Field('photo2', 'upload', length=(130000, 1024), requires=[IS_IMAGE(), IS_LENGTH(130000, 1024)]), 
                Field('title', 'string', length=100,requires=IS_LENGTH(100,2)), 
                Field('subject', 'string', length=25,requires=IS_LENGTH(25,2)), 
                Field('the_good', 'string', length=250,requires=IS_LENGTH(250,2)), 
                Field('the_bad', 'string', length=250,requires=IS_LENGTH(250,2)), 
                Field('type', 'string', length=25,requires=IS_LENGTH(25,2)), 
                Field('date', 'datetime', default=datetime.datetime.now()), 
                Field('text', 'text'),
                Field('rating', 'integer', default=1, requires=IS_IN_SET([1,2,3,4,5]), widget=RatingWidget.widget),
                Field('publish', 'boolean', default=True)
                )


#############
##The following is Open source code modified for this application
##Taken from the "simple comments" web2py plugin.
##No licensing applicable
#############
import datetime

db.define_table('plugin_simple_comments_comment',
                Field('tablename',
                      writable=False,readable=False),
                Field('record_id','integer',
                      writable=False,readable=False),
                Field('body','text', requires=[IS_NOT_EMPTY(), IS_LENGTH(1000, 1)],label=T('Your comment'), widget=SQLFORM.widgets.text.widget),
                Field('created_by',db.auth_user,default=auth.user_id,
                      readable=False,writable=False),
                Field('created_on','datetime',default=datetime.datetime.now(),
                      readable=False,writable=False))
