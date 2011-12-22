# -*- coding: utf-8 -*-

from gluon.storage import Storage
settings=Storage()
settings.enforce_permissions = False
settings.production=False
settings.email_server='localhost:25'
settings.email_sender='you@example.com'
settings.email_login=None
settings.hmac_key='sha512:4df4d407-5ef9-46f4-a3f7-a23b5ce12b37'
