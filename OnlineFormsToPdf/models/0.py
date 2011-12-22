from gluon.storage import Storage
settings = Storage()

settings.migrate = True
settings.title = 'forms2pdf'
settings.subtitle = 'We make pdf forms for you'
settings.author = 'Massimo Di Pierro'
settings.author_email = 'mdipierro@cs.depaul.edu'
settings.keywords = ''
settings.description = ''
settings.database_uri = 'sqlite://storage.sqlite'
settings.security_key = '3dd19cd8-4379-42c5-bd9e-6511836e5033'
settings.email_server = 'localhost'
settings.email_sender = 'you@example.com'
settings.email_login = ''
settings.login_method = 'local'
settings.login_config = ''
settings.layout_theme = 'Pluralism'
