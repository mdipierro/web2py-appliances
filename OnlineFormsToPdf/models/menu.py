
response.title = settings.title
response.subtitle = settings.subtitle
response.meta.author = '%s <%s>' % (settings.author, settings.author_email)
response.meta.keywords = settings.keywords
response.meta.description = settings.description
response.menu = [
    (T('Index'),URL('index')==URL(),URL('index'),[]),
]

if not request.function=='form_fill': response.menu+=[
    (T('New Form'),URL('form_create')==URL(),URL('form_create'),[]),
    (T('My Forms'),URL('form_select')==URL(),URL('form_select'),[]),
]
