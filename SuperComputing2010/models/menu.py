
response.title = settings.title
response.subtitle = settings.subtitle
response.meta.author = '%s <%s>' % (settings.author, settings.author_email)
response.meta.keywords = settings.keywords
response.meta.description = settings.description
response.menu = [
    (T('Index'),URL('index')==URL(),URL('index'),[]),
    (T('Experiment Create'),URL('experiment_create')==URL(),URL('experiment_create'),[]),
    (T('Experiment Select'),URL('experiment_select')==URL(),URL('experiment_select'),[]),
]
