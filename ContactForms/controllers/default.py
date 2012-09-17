# -*- coding: utf-8 -*-
# this file is released under public domain and you can use without limitations

#########################################################################
## This is a samples controller
## - index is the default action of any application
## - user is required for authentication and authorization
## - download is for downloading files uploaded in the db (does streaming)
## - call exposes all registered services (none by default)
#########################################################################

# http://www.web2py.com/book/default/chapter/07#CRUD
from gluon.tools import Crud
crud = Crud(db)

def data(): return dict(form=crud())

#ContactUs
def update_t_contactus00():
    return dict(form=crud.update(db.t_contactus00, request.args(0)))
def update_t_contactus01():
    return dict(form=crud.update(db.t_contactus01, request.args(0)))
def update_t_contactus02():
    return dict(form=crud.update(db.t_contactus02, request.args(0)))
def update_t_contactus03():
    return dict(form=crud.update(db.t_contactus03, request.args(0)))
def update_t_contactus04():
    return dict(form=crud.update(db.t_contactus04, request.args(0)))

#SignUp
def update_t_signup00():
    return dict(form=crud.update(db.t_signup00, request.args(0)))
def update_t_signup01():
    return dict(form=crud.update(db.t_signup01, request.args(0)))
def update_t_signup02():
    return dict(form=crud.update(db.t_signup02, request.args(0)))
def update_t_signup03():
    return dict(form=crud.update(db.t_signup03, request.args(0)))
def update_t_signup04():
    return dict(form=crud.update(db.t_signup04, request.args(0)))

	
#Appointment
def update_t_appointment00():
    return dict(form=crud.update(db.t_appointment00, request.args(0)))
def update_t_appointment01():
    return dict(form=crud.update(db.t_appointment01, request.args(0)))
def update_t_appointment02():
    return dict(form=crud.update(db.t_appointment02, request.args(0)))
def update_t_appointment03():
    return dict(form=crud.update(db.t_appointment03, request.args(0)))

indexMM = '''## Stock Forms for Web2py
### Background
While using the web2py App Wizard, I got frustrated at needing to define the model for a
"Contact Us" form for the *90 millionth time*. So, i made a suggestion in code.google/p/web2py
in Issue 982. **Massimo liked the idea and said, "If you have done work in this direction feel free to post a patch."**

Well, **I didn't have any work already done :)** so I got a little busy **and made this app. :)**

### This app, The Forms App
**Back to work! :)** I went over some of the many forms at jotform.com. I analyzed them for their models from simplest to more complex.
This app, The Forms App as it now stands displays three categories of forms in its menu:
+ Contact Us
+ Sign Up
+ Appointment

I plan to add the ability for web2py users to register and submit: 
+ Forms [model code] in existing Form Categories
+ New Form Categories with at least 3 ascendingly complex models for each category.

Additionally, once a stock form is selected, I think we need to plan a subsequent Wizard Step to add/delete widgets in the form. Such as a captcha widget.
Below is a recap of my suggestion in Issue 982

Love and peace,
Joe

### Issue 982
The App Wizard is a great tool to cut down on the boilerplate development time. I think this suggestion will help productivity even more.

At Step-2 of the App Wizard we define the tables that we will use in the app. I suggest we add the ability to choose from a set pre-defined tables at this step and allow the developer to customize them at a leter step. Here are some examples of tables i have gathered from http://www.jotform.com/form-templates/

I am NOT suggesting we do all of these, however perhaps we could do 1 or 2 in each category.
----
Contact Forms  222 |Application Forms  163 |Abstract Forms  137 |Request Forms  130
Registration Forms  116 |Feedback Forms  101 |Order Forms  96 |Surveys  86
Event Registration Forms  70 |Signup Forms  64 |Booking Forms  59 |Evaluation Forms  56
Reservation Forms  49 |Upload Forms  45 |Report Forms  43 |Membership Forms  41
Tracking Forms  40 |Appointment Form  39 |Employment Forms  36 |Quote Forms  35
Wedding Forms  33 |Award Forms  33 |Lead Generation Forms  33 |Consent Forms  32
Payment Forms  31 |Content Forms  30 |Subscription Forms  26 |Volunteer Forms  24
Donation Forms  14 |Recommendation Forms  13 |Polls  13 |RSVP Forms  11
Petition Forms  9 |Sponsorship Forms  9
----
Thanks for the great work.
Love and peace,
Joe 
'''	
	
	
	
def index():
    """
    example action using the internationalization operator T and flash
    rendered by views/default/index.html or views/generic.html

    if you need a simple wiki simple replace the two lines below with:
    return auth.wiki()
    """
    #response.flash = T("Welcome to web2py!")
    #return dict(message=T('Hello World'))
    return dict(message=MARKMIN(indexMM).xml())

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
