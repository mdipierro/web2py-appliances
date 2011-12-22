import os
from gluon.storage import Storage
settings = Storage()

settings.migrate = True
settings.title = 'web2py'
settings.subtitle = 'sites powered by web2py'
settings.author = 'wizard'
settings.author_email = 'mdipierro@cs.depaul.edu'
settings.keywords = 'web2py, powered'
settings.description = 'Sites powered by web2py'
settings.database_uri = 'sqlite://storage.sqlite'
settings.security_key = '12b982eb-1188-4a42-aa3d-5178f56b6d17'
settings.email_server = 'localhost'
settings.email_sender = 'you@example.com'
settings.email_login = ''
settings.layout_theme = 'solutionblue'
