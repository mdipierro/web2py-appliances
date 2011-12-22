response.title = settings.title
response.subtitle = settings.subtitle
response.meta.author = '%s <%s>' % (settings.author, settings.author_email)
response.meta.keywords = settings.keywords
response.meta.description = settings.description
response.menu = [
    (T('Index'),URL('index')==URL(),URL('index'),[]),
    (T('Create'),URL('appointment_create')==URL(),URL('appointment_create'),[]),
    (T('Select'),URL('appointment_select')==URL(),URL('appointment_select'),[]),
    (T('Map'),URL('mymap')==URL(),URL('mymap'),[]),
    (T('Calendar'),URL('mycal')==URL(),URL('mycal'),[]),

]
