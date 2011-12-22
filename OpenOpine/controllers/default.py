# -*- coding: utf-8 -*-

#########################################################################
##Written by C. S. Schroeder, A Theory of Publishing
##Copyright (C) 2011 Equimind Financial LLC.
##
##Permission is hereby granted, free of charge, to any
##person obtaining a copy of this software and associated
##documentation files (the "Software"), to deal in the
##Software without restriction, including without limitation
##the rights to use, copy, modify, merge, publish,
##distribute, sublicense, and/or sell copies of the
##Software, and to permit persons to whom the Software is
##furnished to do so, subject to the following conditions:
##
##The above copyright notice and this permission notice
##shall be included in all copies or substantial portions of
##the Software.
##
##THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY
##KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE
##WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR
##PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS
##OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR
##OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR
##OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE
##SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
##
##  Powered by web2py, Thanks Massimo!
#########################################################################


try:
    request_arg_1 = request.args[0]
except:
    request_arg_1 = -1


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
    return dict(searchrevs=[], searchprofs=[],tag_form='',form=auth())


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

def quick_search(t=True):
    profurl = [URL(request.application, 'default', 'profiles', vars=dict(tbl='region')),
               URL(request.application, 'default', 'profiles', vars=dict(tbl='place')),
               URL(request.application, 'default', 'profiles', vars=dict(tbl='event')),
               ]
    reviewurl = [URL(request.application, 'default', 'reviews', vars=dict(tbl='region')),
               URL(request.application, 'default', 'reviews', vars=dict(tbl='place')),
               URL(request.application, 'default', 'reviews', vars=dict(tbl='event')),
               ]
    reviews = [[T('Companies'), reviewurl[0]], [T('Products'), reviewurl[1]], [T('Events'), reviewurl[2]]]
    profiles = [ [T('Companies'), profurl[0]],[T('Products'), profurl[1]], [T('Events'), profurl[2]] ]
    return reviews, profiles

def index():
    reviews, profiles = quick_search()
    return dict(searchrevs=reviews, searchprofs=profiles, tag_form='',message=T('Welcome'))

def reviewers():
    search_type = 'reviewers'
    if request_arg_1>0: page = int(request_arg_1)
    else: page = 0
    items_per_page = 12
    limitby=(items_per_page*page, items_per_page*(page+1)+1)
    recs = db().select(db.reviewer.userid, db.reviewer.id, db.reviewer.photo, db.reviewer.city, db.reviewer.about_me, db.reviewer.screenname, limitby=limitby, orderby=~db.reviewer.screenname)
    return dict(searchrevs=[], searchprofs=[],tag_form='', recs=recs, page=page, items_per_page=items_per_page, redirecttype='reviewer_profile', search_type=search_type, message=T('the people'))

def reviewer_profile():
    rec = db(db.reviewer.id==request_arg_1).select(db.reviewer.ALL)
    profile_photo_limit = 10
    if len(rec): rec = rec[0]
    else: redirect(URL(request.application, 'default' ,'reviewers'))
    graphics = []
    for name in ('place','event','region'):
        tablepics = db[name+"_review"]
        photos = db((tablepics.author == request_arg_1)&(tablepics.publish==True)).select(tablepics.ALL)
        graphics += photo_list(photos, min(profile_photo_limit,len(photos)), redirect=name, first="title", secondary="subject")
    return dict(graphics=graphics, searchrevs=[], searchprofs=[],tag_form='', rec=rec, message= rec.screenname)

def reviews():
    search_type = 'review'
    sv = session.tablename
    try:
        session.tablename = request.vars['tbl']
    except:
        session.tablename = sv
    if not (session.tablename in ('place','event','region')): 
        session.tablename = None
        redirect(URL(request.application, 'default', 'index'))
    if request_arg_1>0: page = int(request_arg_1)
    else: page = 0
    items_per_page = 12
    limitby=(items_per_page*page, items_per_page*(page+1)+1)
    table = db[session.tablename+"_"+search_type]
    recs = db(table.publish==True).select(table.id, table.photo, table.blurb, table.title, table.subject, limitby=limitby)
    viewname = tablelabel(session.tablename)
    reviews, profiles = quick_search()
    return dict(searchrevs=[], searchprofs=reviews, tag_form='', recs=recs, page=page, tablename=session.tablename, items_per_page=items_per_page, redirecttype='review', search_type=search_type, message=T('%(tbl)s Reviews', dict(tbl=viewname)))

def process_comments(reftablename, record_id):
    table=db.plugin_simple_comments_comment
    table.tablename.default = reftablename
    table.record_id.default = record_id
    table.body.widget = SQLFORM.widgets.string.widget
    form=SQLFORM(table)
    form.accepts(request.post_vars)
    comments=db((table.tablename==reftablename) & (table.record_id==record_id)).select()
    return comments, form

def review():
    search_type = 'review'
    sv = session.tablename
    try:
        session.tablename = request.vars['tbl']
    except:
        session.tablename = sv
    if not (session.tablename in ('place','event','region')): 
        session.tablename = None
        redirect(URL(request.application, 'default', 'index'))
    if not (request_arg_1>0): redirect(URL(request.application, 'default' ,'reviews', vars=dict(tbl='place')))
    fulltablename = session.tablename+"_"+search_type
    table = db[fulltablename]
    rec = db((table.id==request_arg_1)&(table.publish==True)).select(table.ALL)
    if len(rec): rec = rec[0]
    else: redirect(URL(request.application, 'default' ,'reviews', vars=dict(tbl='place')))
    name = db[session.tablename][rec.ref_id].name
    if auth.is_logged_in():
        comments, form = process_comments(fulltablename, request_arg_1)
    else:
        comments = []
        form = None
    return dict(comments=comments, tablename=session.tablename, form=form, searchrevs=[], searchprofs=[],tag_form='', name = name, rec=rec, message=T('%(title)s: %(subject)s', rec))

def profiles():
    search_type = 'profile'
    sv = session.tablename
    try:
        session.tablename = request.vars['tbl']
    except:
        session.tablename = sv        
    if not (session.tablename in ('place','event','region')): 
        session.tablename = None
        redirect(URL(request.application, 'default', 'index'))
    if request_arg_1>0: page = int(request_arg_1)
    else: page = 0
    session.tablename in ('place','event','region')    
    items_per_page = 12
    limitby=(items_per_page*page, items_per_page*(page+1)+1)
    table = db[session.tablename]
    recs = db().select(table.id, table.photo, table.name, table.about, limitby=limitby)
    viewname = tablelabel(session.tablename)
    reviews, profiles = quick_search()    
    return dict(searchrevs=[], searchprofs=profiles, tag_form='', recs=recs, page=page, items_per_page=items_per_page, redirecttype='profile', search_type=search_type, tablename=session.tablename, message=T('%(tbl)s Profiles', dict(tbl=viewname)))

def profile():
    search_type = 'profile'
    profile_photo_limit = 12
    sv = session.tablename
    try:
        session.tablename = request.vars['tbl']
    except:
        session.tablename = sv
    if not (session.tablename in ('place','event','region')): 
        session.tablename = None
        redirect(URL(request.application, 'default' ,'profiles', vars=dict(tbl='place')))
    if not (request_arg_1>0): redirect(URL(request.application, 'default' ,'profiles', vars=dict(tbl='place')))
    if (session.tablename in ('place','event')): place_or_event = True
    else: place_or_event = False
    table = db[session.tablename]
    rec = db(table.id==request_arg_1).select(table.ALL)
    if len(rec): rec = rec[0]
    else: redirect(URL(request.application, 'default' ,'profiles', vars=dict(tbl='place')))
    rgraphics = []
    egraphics = []
    if not place_or_event:
        rpics = db(db.place.region == request_arg_1).select(db.place.ALL)
        epics = db(db.event.region == request_arg_1).select(db.event.ALL)
        rgraphics = photo_list(rpics, min(profile_photo_limit/3,len(rpics)), redirect='place', photo_field='photo', first='name', secondary=None, random_disp=True, reverse=False)
        egraphics = photo_list(epics, min(profile_photo_limit/3,len(epics)), redirect='event', photo_field='photo', first='name', secondary=None, random_disp=True, reverse=False)
    tablepics = db[session.tablename+"_review"]
    photos = db((tablepics.ref_id == request_arg_1)&(tablepics.publish==True)).select(tablepics.ALL)
    graphics = photo_list(photos, min(profile_photo_limit/3,len(photos)), redirect=session.tablename, first="title", secondary="subject")
    return dict(graphics=graphics, rgraphics=rgraphics, egraphics=egraphics, searchrevs=[], searchprofs=[],tag_form='', place_or_event= place_or_event, rec=rec, message=T('%(name)s', rec))

@auth.requires_membership('reviewer')
def create_profile():
    search_type = "profile"
    sv = session.tablename
    try:
        session.tablename = request.vars['tbl']
    except:
        session.tablename = sv
    if not (session.tablename in ('place','event','region')): 
        session.tablename = None
        redirect(URL(request.application, 'default', 'index'))
    table = db[session.tablename]
    table.id.readable = False
    table.photo.readable = False
    table.about.readable = False
    if session.tablename in ('place', 'event'):
        table.region.represent = lambda id, row: db.region[id].name
    if request.args:
        if request.args[0] == "view":
            if len(request.args)>1:
                redirect(URL(request.application, 'default','profile', args=[request.args[2]], vars=dict(tbl=session.tablename)))
            else:
                session.tablename = None
                redirect(URL(request.application, 'default', 'index'))
        if request.args[0] == "edit":
            table.photo.readable = True
            table.about.readable = True
    
    viewname = tablelabel(session.tablename)
    if session.tablename in ('place', 'event'):
        form = SQLFORM.grid(table, maxtextlength=20, csv=False,\
            headers=dict([(session.tablename+'.name',viewname),(session.tablename+'.blurb', T('Short Description')),(session.tablename+'.region', T("Location"))]), columns=dict([(session.tablename+'.name',20),(session.tablename+'.blurb', 20),(session.tablename+'.region', 20)]))
    else:
        form = SQLFORM.grid(table, maxtextlength=20, csv=False,\
            headers=dict([(session.tablename+'.name',T("Name")),(session.tablename+'.blurb', T('Short Description')),(session.tablename+'.city', T("City")),(session.tablename+'.state', T("State")),(session.tablename+'.country', T("Country"))]), columns=dict([(session.tablename+'.name',15),(session.tablename+'.blurb', 15),(session.tablename+'.city', 15),(session.tablename+'.state', 15),(session.tablename+'.country', 15)]))
    return dict(searchrevs=[], searchprofs=[], tag_form='', form=form,message=T('Create %(tbl)s Profile', dict(tbl=viewname)))

@auth.requires_membership('reviewer')
def create_review():
    search_type = "review"
    sv = session.tablename
    try:
        session.tablename = request.vars['tbl']
    except:
        session.tablename = sv
    if not (session.tablename in ('place','event','region')): 
        session.tablename = None
        redirect(URL(request.application, 'default', 'index'))
    table = db[session.tablename+"_"+search_type]
    table.id.readable = False
    table.photo.readable = False
    table.photo1.readable = False
    table.photo2.readable = False
    table.date.readable = table.date.writable= False
    table.ref_id.represent = lambda id, row: db[session.tablename][id].name
    table.author.represent = lambda auid, row: db.reviewer[auid].screenname
    if request.args:
        if request.args[0] == "view":
            if len(request.args)>1:
                redirect(URL(request.application, 'default','review', args=[request.args[2]], vars=dict(tbl=session.tablename)))
            else:
                session.tablename = None
                redirect(URL(request.application, 'default', 'index'))
        if request.args[0] in ("edit","new"):
            table.author.default = db(db.reviewer.userid == auth.user_id).select(db.reviewer.id).first().id
            if not auth.has_membership('admin'):
                table.author.writable = False
    viewname = tablelabel(session.tablename)
    if auth.has_membership('admin'):
        tablequery = (table.id > 0)
    else: 
        tablequery = (table.author == auth.user_id)
    form = SQLFORM.grid(tablequery, maxtextlength=15, csv=False,\
                        headers=dict([(session.tablename+'_review.ref_id',viewname),(session.tablename+'_review.blurb', T('Short Description')),(session.tablename+'_review.author', T("Reviewer")),(session.tablename+'_review.title', T("Title")),(session.tablename+'_review.subject', T("Subject"))]), columns=dict([(session.tablename+'_review.ref_id',15),(session.tablename+'_review.blurb', 15),(session.tablename+'_review.author', 15),(session.tablename+'_review.title', 15),(session.tablename+'_review.subject', 15)]))
    return dict(searchrevs=[], searchprofs=[],tag_form='', form=form, message=T('Create %(tbl)s Review', dict(tbl=viewname)))

@auth.requires_membership('admin')
def create_contributor():
    addrev = lambda form: auth.add_membership(auth.id_group("reviewer"), int(form.vars.userid))
    delrev = lambda table, itid: auth.del_membership(auth.id_group("reviewer"), table[int(itid)].userid) #ondelete=delrev, db(table.id == int(itid)).select()[0]["userid"]) #
    form = SQLFORM.grid(db.reviewer, oncreate=addrev, ondelete=delrev, csv=False, headers=dict([('reviewer.screenname',T('Display Name')),('reviewer.userid', T('User')),('reviewer.city', T("City")),('reviewer.state', T("State")),('reviewer.country', T("Country"))]), columns=dict([('reviewer.screenname',15),('reviewer.userid', 15),('reviewer.city', 15),('reviewer.state', 15),('reviewer.country', 15)]))
    return dict(searchrevs=[], searchprofs=[],tag_form='', form=form, message=T('Manage Contributors'))

def tablelabel(tablename):
    viewname = ''
    if tablename == 'place':
        viewname=T("Product")
    elif tablename == 'region':
        viewname=T("Company")
    elif tablename == 'event':
        viewname=T("Event")
    else:
        viewname = T("All")
    return viewname

def photo_list(photos, limit, redirect='place', photo_field='photo', first='name', secondary=None, random_disp=True, reverse=False):
    pgraphics = []
    if len(photos)>0: 
        if isinstance(photos, list): pics = photos
        else: pics= photos.as_list()
    else: return pgraphics
    if reverse: pics.reverse()
    if random_disp:
        import random
        last = pics.pop()
        ct = range(0, limit-1)
        ct.reverse()
        for i in ct:
            p = pics.pop(random.randint(0,i))
            pgraphics.append([p['id'], URL(r=request, f='download', args=p[photo_field]), p[first]+', '+p[secondary] if secondary else p[first], redirect])
            if len(pgraphics) == limit:
                break
        pgraphics.append([last['id'], URL(r=request, f='download', args=last[photo_field]), last[first]+', '+last[secondary] if secondary else last[first], redirect])
    else:
        for p in pics:
            pgraphics.append([p['id'], URL(r=request, f='download', args=p[photo_field]), p[first]+', '+p[secondary] if secondary else p[first],redirect])
            if len(pgraphics) == limit:
                break
    return pgraphics
