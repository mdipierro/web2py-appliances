# -*- coding: utf-8 -*-
# this file is released under public domain and you can use without limitations

#########################################################################
## This is a samples controller
## - index is the default action of any application
## - user is required for authentication and authorization
## - download is for downloading files uploaded in the db (does streaming)
## - call exposes all registered services (none by default)
#########################################################################
    
@auth.requires_membership(role='Manager')
def admin():
     "creates a new project"
     projects = db().select(db.project.name, db.project.id )
     formproj = crud.create(db.project)
     formclient = crud.create(db.client)
     return dict(formproj=formproj, projects=projects, searchform=FORM(INPUT(_id='keyword',_name='keyword',
              _onkeyup="ajax('bg_findprojects', ['keyword'], 'target');")),
              target_div=DIV(_id='target'))

@auth.requires_membership(role='Manager')     
def clients():
     clients = db().select(db.client.name, db.client.id, db.client.company)
     formclient = crud.create(db.client)
     return dict(formclient=formclient, clients=clients, searchform=FORM(INPUT(_id='keyword',_name='keyword',
              _onkeyup="ajax('bg_findclient', ['keyword'], 'target');")),
              target_div=DIV(_id='target'))

@auth.requires_membership(role='Manager')
def showclient():
	this_page = db.client(request.args(0)) or redirect(URL('clients'))
	return dict(client=this_page)
@auth.requires_membership(role='Manager')
def allclients():
    clients = db().select(db.client.name, db.client.company, db.client.id)
    return dict(clients=clients)
@auth.requires_login()      
def allprojects():
    projects = db().select(db.project.name, db.project.client, db.project.id)
    return dict(projects=projects)
    
@auth.requires_membership(role='Manager')    
def allemployees():
    employees = db().select(db.employee.name, db.employee.email, db.project.id)
    return dict(employees=employees)

@auth.requires_login()              
def bg_findprojects():
     "an ajax callback that returns a <ul> of links to clients"
     pattern = '%' + request.vars.keyword.lower() + '%'
     project = db(db.project.name.lower().like(pattern))\
       .select(orderby=db.project.name)
     items = [A(row.name, _href=URL('showproject', args=row.id)) \
            for row in project]
     return UL(*items).xml()

@auth.requires_login()              
def bg_findclient():
     "an ajax callback that returns a <ul> of links to clients"
     pattern = '%' + request.vars.keyword.lower() + '%'
     client = db(db.client.name.lower().like(pattern))\
       .select(orderby=db.client.name)
     items = [A(row.name, _href=URL('showclient', args=row.id)) \
            for row in client]
     return UL(*items).xml()
     
@auth.requires_login()              
def bg_findemployee():
     "an ajax callback that returns a <ul> of links to clients"
     pattern = '%' + request.vars.keyword.lower() + '%'
     employee = db(db.employee.name.lower().like(pattern))\
       .select(orderby=db.employee.name)
     items = [A(row.name, _href=URL('showemployee', args=row.id)) \
            for row in employee]
     return UL(*items).xml()
     
@auth.requires_membership(role='Manager') 
def editclient():
     "edit an existing client"
     this_page = db.client(request.args(0))
     form = crud.update(db.client, this_page,
     next = URL('clients', args=request.args))
     return dict(form=form)
     
@auth.requires_membership(role='Manager') 
def editdepartment():
     "edit an existing client"
     this_page = db.department(request.args(0))  or redirect(URL('departments'))
     form = crud.update(db.department, this_page,
     next = URL('departments', args=request.args))
     return dict(form=form)
     
@auth.requires_membership(role='Manager') 
def editproject():
     "edit an existing project"
     this_page = db.project(request.args(0))
     form = crud.update(db.project, this_page,
     next = URL('projects', args=request.args))
     return dict(form=form)
     
@auth.requires_membership(role='Manager')     
def emps():
     emps = db().select(db.employee.name, db.employee.id)
     formemp = crud.create(db.employee)
     return dict(formemp=formemp, emps=emps, searchform=FORM(INPUT(_id='keyword',_name='keyword',
              _onkeyup="ajax('bg_findemployee', ['keyword'], 'target');")),
              target_div=DIV(_id='target'))
     
@auth.requires_membership(role='Manager')     
def depts():
     departments = db().select(db.department.name, db.department.id)
     formdept = crud.create(db.department)
     return dict(formdept=formdept, departments=departments)

@auth.requires_login()    
def projects():
    projects = db().select(db.project.name, db.project.client, db.project.id)
    return dict(projects=projects)
    
    
@auth.requires_login()               
def assest():
    assest = db(db.assest.id==request.args(0)).select().first()
    return dict(assest=assest)


@auth.requires_login()               
def showproject():
	this_page = db.project(request.args(0)) or redirect(URL('allprojects'))
	db.post.page_id.default = this_page.id
	db.assest.page_id.default = this_page.id
	form = crud.create(db.post) if auth.user else "Login to Post to the Project"
	formast = crud.create(db.assest) if auth.user else "Login to Upload Assests to the Project"
	pageposts = db(db.post.page_id==this_page.id).select()
	pageassests = db(db.assest.page_id==this_page.id).select()
	return dict(project=this_page, posts=pageposts, form=form, formast=formast, assests=pageassests)

@auth.requires_login()               
def showdept():
	this_page = db.department(request.args(0)) or redirect(URL('depts'))
	return dict(department=this_page)

@auth.requires_login()  
def index():
	projects = db().select(db.project.name, db.project.client, db.project.id)
	posts = db().select(db.post.post, db.post.created_by, db.post.created_on, db.post.id, db.post.page_id)
	
	return dict(projects=projects, posts=posts)

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

@auth.requires_login()  
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
    return service()


@auth.requires_signature()
def data():
    """
    http://..../[app]/default/data/tables
    http://..../[app]/default/data/create/[table]
    http://..../[app]/default/data/read/[table]/[id]
    http://..../[app]/default/data/update/[table]/[id]
    http://..../[app]/default/data/delete/[table]/[id]
    http://..../[app]/default/data/select/[table]
    http://..../[app]/default/data/search/[table]
    but URLs bust be signed, i.e. linked with
      A('table',_href=URL('data/tables',user_signature=True))
    or with the signed load operator
      LOAD('default','data.load',args='tables',ajax=True,user_signature=True)
    """
    return dict(form=crud())
