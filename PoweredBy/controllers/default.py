# -*- coding: utf-8 -*- 
### required - do no delete
def user(): return dict(form=auth())
def download(): return response.download(request,db)
def call():
    session.forget()
    return service()
### end requires
def index():
    import os
    #path = os.path.join(request.folder,'static','thumbnails')
    #files=os.listdir(path)
    #db(db.t_site.id.belongs((4,5,11,14,17,22,26,27,28,29,31,32,34,37,42,51,52))).delete()
    #for file in files:
    #    db.t_site.insert(f_url='http://'+file[:-4],f_name=file[:-4],
    #                     f_description='')    
    sites=db(db.t_site.f_featured==True).select(orderby='<random>')
    sites=sites|db(db.t_site.f_featured==False).select(orderby='<random>')
    #for site in sites:
    #    filename=site.f_name+'.jpg'
    #    file=os.path.join(request.folder,'static','thumbnails',filename)
    #    site.update_record(f_image=db.t_site.f_image.store(open(file,'rb'),filename))
    return dict(sites=sites)

def images():
    n = int(request.args(0) or 100)
    sites = db(db.t_site.f_featured==True).select(orderby='<random>',limitby=(0,n))
    return response.json(['http://web2py.com/poweredby/default/download/%s' % s.f_image for s in sites])
    
@auth.requires_login()
def site_create():
    form=crud.create(db.t_site,next='index')
    return dict(form=form)

@auth.requires_login()
def site_read():
    record = db.t_site(request.args(0)) or redirect(URL('error'))
    form=crud.read(db.t_site,record)
    return dict(form=form)

@auth.requires_login()
def site_update():
    editor = auth.user and auth.user.editor
    if editor:
        db.t_site.f_featured.writable=True
        db.t_site.f_created_on.readable=True
        db.t_site.f_modified_on.readable=True
    record = db.t_site(request.args(0)) or redirect(URL('error'))
    if(record.f_created_by!=auth.user_id and not editor):
		redirect(auth.settings.on_failed_authorization)
    form=crud.update(db.t_site,record,next='index')
    created_by = '%(first_name)s %(last_name)s, %(email)s' % db.auth_user(db.auth_user.id==record.f_created_by).as_dict()
    modified_by = '%(first_name)s %(last_name)s, %(email)s' % db.auth_user(db.auth_user.id==record.f_modified_by).as_dict()
    return dict(form=form, editor=editor, created_by=created_by, modified_by=modified_by)

