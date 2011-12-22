# coding: utf8

#########################################################################
## This is a samples controller
## - index is the default action of any application
## - user is required for authentication and authorization
## - download is for downloading files uploaded in the db (does streaming)
## - call exposes all registered services (none by default)
#########################################################################  

def index():
    rows=db(db.dna.id).select(db.dna.id,db.dna.name)
    return dict(rows=rows)

def gene_size():
    dna = db.dna[request.vars.id] or redirect(URL('index'))
    lenghts = find_gene_size(dna.sequence)
    return hist(title=dna.name,data={'Lenghts':lenghts})

@auth.requires_login()
def needleman_wunsch_plot():
    dna1 = db.dna[request.vars.sequence1]
    dna2 = db.dna[request.vars.sequence2]
    z = needleman_wunsch(dna1.sequence,dna2.sequence)
    return pcolor2d(z=z)

@auth.requires_login()
def compare():
    form = SQLFORM.factory(
        Field('sequence1',db.dna,requires=IS_IN_DB(db,'dna.id','%(name)s')),
        Field('sequence2',db.dna,requires=IS_IN_DB(db,'dna.id','%(name)s')))
    if form.accepts(request):
        image=URL('needleman_wunsch_plot',vars=form.vars)
    else:
        image=None
    return dict(form=form, image=image)

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
