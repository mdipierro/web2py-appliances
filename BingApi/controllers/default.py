#########################################################################
## This is a samples controller
## - index is the default action of any application
## - user is required for authentication and authorization
## - download is for downloading files uploaded in the db (does streaming)
## - call exposes all registered services (none by default)
#########################################################################  

from bingapi_w import Bing
BING_APPID='25187A3B438492061BC2B82AB10E1D7394F0EB82'

response.title="Bing Interface"
response.subtitle="Full Web Search from web2py"

def index():
    """
    example action using the internationalization operator T and flash
    rendered by views/default/index.html or views/generic.html
    """
    form=FORM(INPUT(_name='q',requires=IS_NOT_EMPTY()),
              INPUT(_type='submit',_value='Search'))
    items=[]
    if form.accepts(request,session):
        bing = Bing(BING_APPID)
        res = bing.do_web_search(request.vars.q)
        items = res['SearchResponse']['Web']['Results']
    return dict(form=form,items=items)

def download():
    """
    allows downloading of uploaded files
    http://..../[app]/default/download/[filename]
    """
    return response.download(request,db)
