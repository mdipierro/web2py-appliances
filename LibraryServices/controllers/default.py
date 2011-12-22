# -*- coding: utf-8 -*- 

#########################################################################
## This is a samples controller
## - index is the default action of any application
## - user is required for authentication and authorization
## - download is for downloading files uploaded in the db (does streaming)
## - call exposes all registered services (none by default)
#########################################################################  

def index():
    """
    example action using the internationalization operator T and flash
    rendered by views/default/index.html or views/generic.html
    """
    form=FORM(INPUT(_name='keywords',requires=IS_NOT_EMPTY()),_method='GET')
    if form.accepts(request):
        keywords = form.vars.keywords.split()
        query1 = reduce(lambda a,b:a|b,[db.book.authors.like('%'+key+'%') for key in keywords])
        query2 = reduce(lambda a,b:a|b,[db.book.title.like('%'+key+'%') for key in keywords])
        query3 = reduce(lambda a,b:a|b,[db.book.isbn13.like('%'+key+'%') for key in keywords])
        books = db(query1|query2|query3).select(orderby=db.book.title|~db.book.publication_year)
    else:
        books=None
    if books and len(books)==1:
        redirect(URL('book',args=books.first().id))
    return dict(form=form,books=books)

def book():
    book = db.book[request.args(0)] or redirect(URL('index'))
    loans = db(db.loan.book==book.id)(db.loan.loan_end>request.now).select(orderby=db.loan.loan_start)
    return dict(form=crud.read(db.book,book),book=book,loans=loans)

@auth.requires(librarian)
def edit():
    book = db.book[request.args(0)]
    form = crud.update(db.book,book,next=URL('book',args=book.id))
    return dict(form=form,book=book)

@auth.requires(librarian)
def loan():
    book = db.book[request.args(0)] or redirect(URL('index'))
    db.loan.book.default = book.id
    db.loan.book.writable = False
    form = crud.update(db.loan,request.args(1),next=URL('book',args=book.id))
    return dict(form=form,book=book)

def user():
    """
    exposes:
    http://..../[app]/default/user/login 
    http://..../[app]/default/user/logout
    http://..../[app]/default/user/register
    http://..../[app]/default/user/profile
    http://..../[app]/default/user/retrieve_password
    http://..../[app]/default/user/change_password
    use @auth.requires_login()
        @auth.requires_membership('group name')
        @auth.requires_permission('read','table name',record_id)
    to decorate functions that need access control
    """
    return dict(form=auth())


def download():
    """
    allows downloading of uploaded files
    http://..../[app]/default/download/[filename]
    """
    return response.download(request,db)


def call():
    """
    exposes services. for example:
    http://..../[app]/default/call/jsonrpc
    decorate with @services.jsonrpc the functions to expose
    supports xml, json, xmlrpc, jsonrpc, amfrpc, rss, csv
    """
    session.forget()
    return service()
