# -*- coding: utf-8 -*-


def index():
    db.survey.description.readable=False
    db.survey.choices.readable=False
    # db.survey.name.represent = lambda name,row: A(name,_href=URL('take_survey',args=row.uuid))
    grid = SQLFORM.grid(db.survey.created_by==auth.user_id,create=False,editable=False,deletable=True,details=False,
                        links=[lambda row: A('take',_href=URL('take_survey',args=row.uuid),_class="btn"),
                               lambda row: A('results',_href=URL('see_results',args=row.uuid),_class="btn")])
    return locals()

@auth.requires_login()
def create_survey():
    def f(form):
        form.vars.results = [0]*len(request.vars.choices)
    from gluon.utils import web2py_uuid
    db.survey.uuid.default = uuid = web2py_uuid()
    form = SQLFORM(db.survey).process(onvalidation=f)
    if form.accepted:
        redirect(URL('take_survey',args=uuid))
    return locals()

def take_survey():
    uuid = request.args(0)
    survey = db.survey(uuid=uuid) or redirect(URL('index'))
    if survey.requires_login:
        if not auth.user:
             redirect(URL('user/login',vars=dict(_next=URL(args=uuid))))
        vote = db.vote(survey=survey.id,created_by=auth.user.id)
        if vote:
             session.flash = 'You voted already!'
             redirect(URL('thank_you'))
    if request.post_vars:
         k = int(request.post_vars.choice)
         survey.results[k]+=1
         survey.update_record(results=survey.results)
         if survey.requires_login:
             db.vote.insert(survey=survey.id)
         redirect(URL('thank_you'))
    return locals()

@auth.requires_login()
def see_results():
    uuid = request.args(0)
    survey = db.survey(uuid=uuid) or redirect(URL('index'))
    if survey.created_by!=auth.user.id:
        session.flash = 'User not authorized'
        redirect(URL('index'))
    return locals()

def thank_you():
    return dict()

def user():
    """
    exposes:
    http://..../[app]/default/user/login
    http://..../[app]/default/user/logout
    http://..../[app]/default/user/register
    http://..../[app]/default/user/profile
    http://..../[app]/default/user/retrieve_password
    http://..../[app]/default/user/change_password
    http://..../[app]/default/user/manage_users (requires membership in
    use @auth.requires_login()
        @auth.requires_membership('group name')
        @auth.requires_permission('read','table name',record_id)
    to decorate functions that need access control
    """
    return dict(form=auth())

@cache.action()
def download():
    """
    allows downloading of uploaded files
    http://..../[app]/default/download/[filename]
    """
    return response.download(request, db)


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
    but URLs must be signed, i.e. linked with
      A('table',_href=URL('data/tables',user_signature=True))
    or with the signed load operator
      LOAD('default','data.load',args='tables',ajax=True,user_signature=True)
    """
    return dict(form=crud())
