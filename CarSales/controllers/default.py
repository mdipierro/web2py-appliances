# -*- coding: utf-8 -*- 

#########################################################################
## This is a samples controller
## - index is the default action of any application
## - user is required for authentication and authorization
## - download is for downloading files uploaded in the db (does streaming)
## - call exposes all registered services (none by default)
#########################################################################  

def index():
    
    #flashes just one time
    if not session.flashed:
       response.flash=T('Welcome to carshop')
       session.flashed=True
    
    #queries all cars
    query=db.car.id>0
    order=db.car.id
    rows=db(query).select(orderby=order)    
    
    return dict(showcase=SHOWCASE(rows), title='Best Price')


def cars():
    
    #take the arg or redirect
    status=request.args(0) or redirect(URL('index'))
    
    #Just which are in the list
    if status not in ['used', 'new', 'Used', 'New']:
        redirect(URL('index'))
    
    #define the view to render
    response.view='default/index.html'
    
    #query filtered
    query=db.car.status==status.capitalize()        
    order=db.car.id
    rows=db(query).select(orderby=order)            
    
    #cria os objetos de retorno        
    showcase=SHOWCASE(rows)
    title='%s Cars' % status.capitalize()
    
    return dict(showcase=showcase, title=title)


def details():
    
    #take arg or redirect
    id = request.args(0) or redirect(URL('index'))
    
    #query filtered
    query =db.car.id==int(id)
    rows=db(query).select()   
    
    #return object
    showcase = SHOWCASE(rows)
    
    # if has data creates other objects   
    if rows:
        
        #page Title   
        row = rows[0]                  
        title = "%(brand)s - %(model)s - %(year)s - %(state)s" % \
            dict(brand=row.brand.name,\
                 model=row.model,\
                 year=row.year,\
                 state=row.status)
        
        #Form config            
        db.client.id_car.default = id
        db.client.id_car.readable = False
        db.client.id_car.writable = False 
        
        #cretes the form       
        form = SQLFORM(db.client,formstyle='divs',submit_button='Send')
        
        #validation of the form   
        if form.accepts(request, session):
            
            try:
                subject='Client %s wants to buy %s ' % (form.vars.name,form.vars.id_car)
                email_user(sender=form.vars.email,\
                           message='Tel: %s - Finance? %s - Change? %s - Date: %s '\
                                    % (form.vars.tel,form.vars.finance,form.vars.change,form.vars.date),\
                           subject=subject)
            except Exception, e:
                pass               
                  
            response.flash = 'Accepted'
            
            #Success Message
            form = DIV(H3('Message sent, we will contact you soon'))
                
        elif form.errors:
            response.flash = 'Errors'
                                        
        return dict(showcase=showcase,title=title,form=form)
        
    else:
        return dict(showcase=H1('car not found'))                 
    

def search():
    """ Ajax Callback"""
    
    #takes typed value
    txt = request.vars.search
    
    #if not null
    if txt:
        
        #queries with %LIKE% ****HERE BE THE DRAGONS!!!!******
        rows = db(db.car.model.like('%'+txt+'%')).select()
        
        #returns <ul><li>..
        return XML(UL(*[LI(A('%s - %s ' % (row.model,row.year),_href=URL('details',args=row.id)))\
                    for row in rows]))
                    
    else:
        return ''
    
@auth.requires_login()    
def admin():
    args = request.args
    title = 'administration'
    if not args:
        link = UL(*[LI(A(tab,_href=URL(args=tab))) for tab in db.tables])
        return dict(items=link,title=title)
    
    if not args(1):
        i = 0
    else:
        i =1
    
    for tab in db.tables:
        if tab==args(i):
            tb = db[tab]    
    
    if args(0)=='edit':
        form = crud.update(tb, args(2),next=URL(f='admin',args=args(1)))
        items = None
        title = 'Edit %s ' % args(i)
    else:
        form = crud.create(tb)
        rows = db().select(tb.ALL) 
        items = SQLTABLE(rows,linkto='edit')
        title = 'Insert %s ' % args(i)        
    

    return dict(form=form,items=items,title=title)

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
