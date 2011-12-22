
response.title = settings.title
response.subtitle = settings.subtitle
response.meta.author = '%s <%s>' % (settings.author, settings.author_email)
response.meta.keywords = settings.keywords
response.meta.description = settings.description
response.menu = [
    (T('Index'),URL('index')==URL(),URL('index'),[]),
    (T('Site Create'),URL('site_create')==URL(),URL('site_create'),[]),
    (T('About'),False,'http://web2py.com')
]
