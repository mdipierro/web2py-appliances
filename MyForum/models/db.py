# -*- coding: utf-8 -*-

DEBUG = True

db = DAL('sqlite://storage.sqlite',pool_size=1,check_reserved=['all'])

response.generic_patterns = ['*'] if request.is_local else []
from gluon.tools import Auth, Service, prettydate
auth = Auth(db)
auth.define_tables(username=False, signature=False)
service = Service()

## configure email
mail = auth.settings.mailer
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
use_janrain(auth, filename='private/janrain.key')

