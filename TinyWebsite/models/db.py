# -*- coding: utf-8 -*-

#########################################################################
## This scaffolding model makes your app work on Google App Engine too
## File is released under public domain and you can use without limitations
#########################################################################

## if SSL/HTTPS is properly configured and you want all HTTP requests to
## be redirected to HTTPS, uncomment the line below:
# request.requires_https()

from gluon.custom_import import track_changes
from gluon.scheduler import Scheduler
#turn on the auto-reload feature for modules
track_changes(True)

if not request.env.web2py_runtime_gae:
    ## if NOT running on Google App Engine use SQLite or other DB
    db = DAL('sqlite://storage.sqlite', pool_size=1, lazy_tables=True, migrate=True)
    db_sched = DAL('sqlite://storage_scheduler.sqlite')
else:
    ## connect to Google BigTable (optional 'google:datastore://namespace')
    db = DAL('google:datastore')
    ## store sessions and tickets there
    ## or store session in Memcache, Redis, etc.
    ## from gluon.contrib.memdb import MEMDB
    ## from google.appengine.api.memcache import Client
    ## session.connect(request, response, db = MEMDB(Client()))   

scheduler = Scheduler(db_sched)

session.connect(request, response, db=db)
    
## by default give a view/generic.extension to all actions from localhost
## none otherwise. a pattern can be 'controller/function.extension'
# response.generic_patterns = ['*'] if request.is_local else ['*.rss']
response.generic_patterns = ['*.rss']
## (optional) optimize handling of static files
#response.optimize_css = 'concat,minify,inline'
#response.optimize_js = 'concat,minify,inline'

from gluon.tools import Auth, Crud, Service, PluginManager, prettydate

auth = Auth(db)
crud, service, plugins = Crud(db), Service(), PluginManager()

# Custom fields in auth
auth.settings.extra_fields['auth_user']= [
    Field('can_edit_password', 'boolean', default=True, label=T('User can edit his password')),
    Field('can_edit_profile', 'boolean', default=True, label=T('User can edit his profile'))
    ]

## create all tables needed by auth if not custom tables
auth.define_tables(username=True, signature=False)

## configure auth policy
auth.settings.registration_requires_verification = False
auth.settings.registration_requires_approval = False
auth.settings.reset_password_requires_verification = True
if auth.user:
    if not auth.user.can_edit_password:
        auth.settings.actions_disabled.append('change_password')
    if not auth.user.can_edit_profile:
        auth.settings.actions_disabled.append('profile')

## if you need to use OpenID, Facebook, MySpace, Twitter, Linkedin, etc.
## register with janrain.com, write your domain:api_key in private/janrain.key
#from gluon.contrib.login_methods.rpx_account import use_janrain
#use_janrain(auth, filename='private/janrain.key')

class ManagerToolbar():
    def __init__(self, object_name):
        self.object_name=object_name
        self.add_label=T('Add a new %(object)s', dict(object=self.object_name))
        self.update_label=T('Update current %(object)s', dict(object=self.object_name))
        self.delete_label=T('Delete current %(object)s', dict(object=self.object_name))

    def __call__(self, _id=0, container_id=0):
        if _id > 0:
            self.update_url=URL('edit_'+self.object_name, args=_id, extension=False) #extension=False to avoid having a .load extension from inside a controller
            self.delete_url=URL('delete_'+self.object_name, args=_id, extension=False)
            self.toolbar=A(I('',_class='icon-edit icon-large icon-border',
                _title=self.update_label),_href= self.update_url)
            self.toolbar+=A(I('',_class='icon-remove icon-large icon-border',
                _title=self.delete_label),_href=self.delete_url)
            
            
        else:
            self.add_url=URL('edit_'+self.object_name, vars=dict(container_id=container_id), extension=False) #extension=False to avoid having a .load extension from inside a controller
            self.toolbar=A(I('',_class='icon-plus icon-large icon-border',
                _title=self.add_label),_href=self.add_url)
        return self.toolbar
