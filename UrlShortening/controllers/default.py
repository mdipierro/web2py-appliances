def index():
    return dict()

@auth.requires_login()
def bookmark():
    """ allows users to bookmark a page an get short url """
    url = request.vars.url
    link = Link(url=url) or Link.insert(url=url)
    link.update_record(screenshot=thumbalizr(url))
    bid = Bookmark(link=link) or Bookmark.insert(link=link)
    rating = cache.ram(link.url,lambda:wotrate(link.url),3600)
    form = SQLFORM(Bookmark,bid).process(next='bookmarks')
    return locals()

def visit():
    """ tracks visitors """
    link = Link(toInt(request.args(0)))
    link.update_record(visits=Link.visits+1)
    redirect(link.url)

@auth.requires_login() # or requires_membership or requires_permission
def bookmarks():
    """ allow users to manage their bookmarks """
    query = (Bookmark.created_by==auth.user.id)&(Bookmark.link==Link.id)
    grid = SQLFORM.grid(query, create=False)
    return locals()

# stuff required for authentication and access control
def user(): return dict(form=auth())
def download(): return response.download(request,db)
