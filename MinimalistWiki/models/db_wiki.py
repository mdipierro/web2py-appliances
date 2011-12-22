from gluon.contrib.markdown import WIKI

db.define_table('page', 
      Field('name', writable=False),
      Field('author', db.auth_user, readable=False, writable=False),
      Field('saved_on', 'datetime', readable=False, writable=False),
      Field('title'),
      Field('body', 'text'),
      Field('change_note', length=200))

db.page.name.requires=IS_NOT_IN_DB(db,'pages.name')

def get_pages(limitby=(0,1)):
    if not request.args(0): request.args.append('main')
    page_name = request.args(0) or 'main'
    qset=db(db.page.name==page_name)
    if request.vars._version:
        qset=db(db.page.id==request.vars._version)
    pages = qset.select(orderby=~db.page.saved_on,limitby=limitby)
    if pages and pages.first().name!=page_name:
        raise HTTP(404)
    return pages
