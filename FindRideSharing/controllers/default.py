
# # sample index page with internationalization (T)
home=URL('index')

response.menu=[['Home',False,home]]
if auth.user:
    response.menu.append(['Your posts',False,URL('posts')])
    response.menu.append(['Change password',False,URL('user/change_password')])
    response.menu.append(['Logout',False,URL('user/logout')])
else:
    response.menu.append(['Login',False,URL('user/login')])
    response.menu.append(['Register',False,URL('user/register')])
    response.menu.append(['Lost password',False,URL('user/retrieve_password')])

def index():
    items=db().select(db.item.ALL,orderby=~db.item.posted_on,limitby=(0,10))
    return dict(items=items)

def search():
    r='OFFER' if request.args(0)=='NEED' else 'NEED'
    items=db((db.item.location==request.vars.location)&(db.item.request==r))\
        .select(orderby=~db.item.posted_on)
    return dict(items=items)

@auth.requires_login()
def create():
    db.item.request.default=request.args(0)
    return dict(form=crud.create(db.item,next='posts',\
      onaccept=lambda form:auth.add_permission(0,'update',db.item,form.vars.id)))

@auth.requires_permission('update',db.item,item_id)
def update():
    return dict(form=crud.update(db.item,item_id,next='posts'))

@auth.requires_permission('update',db.item,item_id)
def delete():
    del db.item[item_id]
    redirect(URL('posts'))

@auth.requires_login()
def posts():
    items=db(db.item.posted_by==user_id).select()
    return dict(items=items)

# # uncomment the following if you have defined "auth" and "crud" in models
def user(): return dict(form=auth())
# def data(): return dict(form=crud())
def download(): return response.download(request,db)
# # tip: use @auth.requires_login, requires_membership, requires_permission
