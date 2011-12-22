# -*- coding: utf-8 -*-
### required - do no delete
def user(): return dict(form=auth())
def download(): return response.download(request,db)
def call():
    session.forget()
    return service()
### end requires
def index():
    return dict()

def error():
    return dict()

@auth.requires_login()
def mymap():
    rows=db(db.t_appointment.created_by==auth.user.id)(db.t_appointment.f_start_time>=request.now).select()
    return dict(rows=rows)

@auth.requires_login()
def mycal():
    rows=db(db.t_appointment.created_by==auth.user.id).select()
    return dict(rows=rows)

@auth.requires_login()
def appointment_create():
    form=crud.create(db.t_appointment,
                     onvalidation=geocode2,
                     next='appointment_read/[id]')
    return dict(form=form)

@auth.requires_login()
def appointment_read():
    record = db.t_appointment(request.args(0)) or redirect(URL('error'))
    form=crud.read(db.t_appointment,record)
    return dict(form=form)

@auth.requires_login()
def appointment_update():
    record = db.t_appointment(request.args(0),active=True) or redirect(URL('error'))
    form=crud.update(db.t_appointment,record,next='appointment_read/[id]',
                     onvalidation=geocode2,
                     ondelete=lambda form: redirect(URL('appointment_select')),
                     onaccept=crud.archive)
    return dict(form=form)

@auth.requires_login()
def appointment_select():
    f,v=request.args(0),request.args(1)
    query=f and db.t_appointment[f]==v or db.t_appointment
    rows=db(query)(db.t_appointment.active==True).select()
    return dict(rows=rows)

@auth.requires_login()
def appointment_search():
    form, rows=crud.search(db.t_appointment,query=db.t_appointment.active==True)
    return dict(form=form, rows=rows)
