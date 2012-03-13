@service.json
@service.xml
@service.jsonrpc
@service.xmlrpc
@service.amfrpc3('domain')
@service.soap()
def linksby(key=''):
    return db(Link.id==Bookmark.link)\
        (Bookmark.tags.contains(key)).select(Link.ALL,distinct=True)

@request.restful()
def api():
    def POST():
        raise HTTP(501)
    def GET(key=''):
        return dict(result=linksby(key).as_list())
    return locals()

def call(): return service()
