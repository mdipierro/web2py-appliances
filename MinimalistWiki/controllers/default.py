def index():
    return dict(page=get_pages().first())
    
@auth.requires_login()
def edit():
    old_page = get_pages().first()
    if old_page:
        db.page.title.default=old_page.title
        db.page.body.default=old_page.body
    db.page.name.default=request.args(0)
    db.page.author.default=auth.user.id
    db.page.saved_on.default=request.now
    form=crud.create(db.page,next=URL('index',args=request.args))
    return dict(form=form)

def log():
    pages = get_pages(limitby=None)
    return dict(pages=pages)

def user(): return dict(form=auth())

def download(): return response.download(request,db)

def data(): return service()
