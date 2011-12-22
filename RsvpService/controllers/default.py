# -*- coding: utf-8 -*-

@auth.requires_login()  
def create_event():
    if request.args(0):
       event = db.event(request.args(0),created_by=auth.user_id) or redirect(URL('index'))      
       rows = db(db.rsvp.event==event.id).select()  
    else: event, rows=None, []
    form = SQLFORM(db.event,event,deletable=True)
    if form.process().accepted:
        session.flash="record created"
        redirect(URL('index'))
    return locals()
  
@auth.requires_login()      
def index():
    rows = db(db.event.created_by==auth.user_id).select()
    return locals()    
 
@auth.requires_login()    
def respond_event():
    event = db.event(uuid=request.args(0)) or redirect(URL('index'))
    db.rsvp.event.default=event.id
    db.rsvp.event.writable = False
    db.rsvp.attendee.default=auth.user_id
    db.rsvp.attendee.writable=False
    rsvp = db.rsvp(event=event.id,attendee=auth.user_id)
    form = SQLFORM(db.rsvp, rsvp)
    if form.accepts(request,session):
        response.flash="thanks for your response"        
    rows = db(db.rsvp.event==event.id).select()
    return locals()    

def user():
    return dict(form=auth())

def download():
    return response.download(request,db)
