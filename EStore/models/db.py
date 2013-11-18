# -*- coding: utf-8 -*-

#if request.function in ('user','pay'): request.requires_https()

db = DAL(DBURI,pool_size=10,check_reserved=['all'])

# response.optimize_css = 'concat,minify,inline'
# response.optimize_js = 'concat,minify,inline'

from gluon.tools import Auth
auth = Auth(db)

## configure email
mail = auth.settings.mailer
mail.settings.server = EMAIL_SERVER
mail.settings.sender = EMAIL_SENDER
mail.settings.login = EMAIL_LOGIN

## configure auth policy
auth.settings.registration_requires_verification = False
auth.settings.registration_requires_approval = False
auth.settings.reset_password_requires_verification = True

## if you need to use OpenID, Facebook, MySpace, Twitter, Linkedin, etc.
## register with janrain.com, write your domain:api_key in private/janrain.key
from gluon.contrib.login_methods.rpx_account import use_janrain
use_janrain(auth, filename='private/janrain.key')
