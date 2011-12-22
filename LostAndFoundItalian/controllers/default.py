
# # sample index page with internationalization (T)
home=URL('index')

response.menu=[['Cerca',False,home]]
if auth.user:
    response.menu.append(['Tuoi Messaggi',False,URL('posts')])
    response.menu.append(['Cambia Password',False,URL('user/change_password')])
    response.menu.append(['Logout',False,URL('user/logout')])
else:
    response.menu.append(['Login',False,URL('user/login')])
    response.menu.append(['Registrati',False,URL('user/register')])
    response.menu.append(['Perso Password',False,URL('user/retrieve_password')])

def geo(form):
    (form.vars.longitude,form.vars.latitude)=geocode(form.vars.xwhere+', Italy')



def index():
    items=db().select(db.item.ALL,orderby=~db.item.posted_on,limitby=(0,10))
    return dict(items=items)

def search():
    if not request.vars.query or not request.args \
       or not request.args[0] in tr \
       or len(request.vars.query)<3:
        session.flash="Toppi risultati"
        redirect(home)
    keywords=request.vars.query.split(' ')
    query1=[db.item.xwhat.like('%%%s%%' % key)|\
            db.item.xwhere.like('%%%s%%' % key)|\
            db.item.description.like('%%%s%%' % key) for key in keywords]
    query=query1[0]
    items=db((db.item.category==request.args[0])&(query)).select(orderby=~db.item.posted_on)
    return dict(items=items)

@auth.requires_login()
def create():
    db.item.category.default=request.args[0] if request.args else redirect(home)
    return dict(form=crud.create(db.item,next='read/[id]',
                                 onvalidation=geo,
                                 onaccept=lambda form:auth.add_permission(auth.user_group(),'update',db.item,form.vars.id)))

def read():
    return dict(item=db.item[item_id] or redirect(home))

@auth.requires_permission('update',db.item,item_id)
def update():
    return dict(form=crud.update(db.item,item_id,next='read/[id]',
                                 onvalidation=geo))

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
