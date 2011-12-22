# -*- coding: utf-8 -*-
db = DAL('sqlite://storage.sqlite')

from gluon.tools import *
mail = Mail()                 # mailer
auth = Auth(globals(),db)     # authentication/authorization
crud = Crud(globals(),db)     # for CRUD helpers using auth
service = Service(globals())  # for json, xml, jsonrpc, xmlrpc, amfrpc
plugins = PluginManager()

mail.settings.server = 'localhost'
mail.settings.sender = auth.user and auth.user.email or 'massimo.dipierro@gmail.com'
mail.settings.login = None

auth.settings.hmac_key = 'sha512:lkvqoicg832b83bpiquwged7weplwefg'
auth.define_tables()
auth.settings.mailer = mail
auth.settings.registration_requires_verification = False
auth.settings.registration_requires_approval = False
auth.messages.verify_email = 'Click on the link http://'+request.env.http_host+URL('default','user',args=['verify_email'])+'/%(key)s to verify your email'
auth.settings.reset_password_requires_verification = True
auth.messages.reset_password = 'Click on the link http://'+request.env.http_host+URL('default','user',args=['reset_password'])+'/%(key)s to reset your password'
