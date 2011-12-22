# -*- coding: utf-8 -*- 
### required - do no delete
def user(): return dict(form=auth())
def download(): return response.download(request,db)
def call():
    session.forget()
    return service()


def index():
    form=FORM(INPUT(_name="s",_id="s",_size="15"),
              BR(),INPUT(_type="submit",_value="Go"),
              _id="searchform")
    if form.accepts(request):
        forms=db(db.t_form.f_name.contains(form.vars.s)).select(limitby=(0,20))
    else:
        forms=[]
    return dict(form=form, forms=forms)

def error():
    return dict()

@auth.requires_login()
def form_create():
    form=crud.create(db.t_form,next='form_read/[id]')
    return dict(form=form)

@auth.requires_login()
def form_read():
    record = db.t_form(request.args(0)) or redirect(URL('error'))
    form=crud.read(db.t_form,record)
    return dict(form=form,record=record)

@auth.requires_login()
def form_fill():
    extra=dict(
        input_text= lambda x: '<input name="%s" class="string"/>' % x,
        input_date= lambda x: '<input name="%s" id="%s" class="date"/>' % (x,x),
        input_bool= lambda x: '<input type="checkbox" name="%s"/>' % x,
        input_area= lambda x: '<br/><textarea name="%s"></textarea><br/>' % x,
        )
    record = db.t_form(f_uuid=request.args(0)) or redirect(URL('error'))
    form=FORM(MARKMIN(record.f_content,extra=extra),
        INPUT(_type="submit"))
    if form.accepts(request):
        session.form_vars=request.vars  
        redirect(URL('form_get',args=record.f_uuid))     
    return dict(form=form)

    
@auth.requires_login()
def form_get():
    from gluon.contrib.markmin.markmin2pdf import markmin2pdf
    response.headers['Content-Type']='application/pdf'    
    extra=dict(
        input_text= lambda x: session.form_vars.get(x,''),
        input_date= lambda x: session.form_vars.get(x,''),
        input_bool= lambda x: session.form_vars.get(x,'') and '[yes]' or '[no]',
        input_area= lambda x: '\n\n'+session.form_vars.get(x,'')+'\n\n',
        )
    record = db.t_form(f_uuid=request.args(0)) or redirect(URL('error'))
    pdf,warnings,errors=markmin2pdf(record.f_content,extra=extra)
    return pdf

@auth.requires_login()
def form_update():
    record = db.t_form(request.args(0),f_created_by=auth.user_id) or redirect(URL('error'))
    form=crud.update(db.t_form,record,next='form_read/[id]')
    return dict(form=form)

@auth.requires_login()
def form_select():
    db.t_form.f_content.readable=False
    query=db.t_form.f_created_by==auth.user_id
    rows=db(query).select(orderby=db.t_form.f_name)
    return dict(rows=rows)

@auth.requires_login()
def form_search():
    form, rows=crud.search(db.t_form)
    return dict(form=form, rows=rows)
