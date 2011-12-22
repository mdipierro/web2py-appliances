from gluon.storage import Storage
settings = Storage()

settings.migrate = True
settings.title = request.application
settings.subtitle = T('steve van christie')
settings.author = 'steve van christie'
settings.author_email = 'you@example.com'
settings.keywords = 'steve van christie'
settings.description = 'steve van christie'
settings.layout_theme = 'Default'
settings.database_uri = 'sqlite://storage.sqlite'
settings.security_key = 'c4d5c7ec-97b4-474b-98d3-9c1582dad510'
settings.email_server = 'localhost'
settings.email_sender = 'you@example.com'
settings.email_login = ''
settings.login_method = 'local'
settings.login_config = ''
settings.plugins = []
