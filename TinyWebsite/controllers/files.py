from controllers_tools import sizeof_file

def files():
    """
    Allows to access the "files" component
    """
    manager_toolbar = ManagerToolbar('file')
    page = db.page(request.vars.container_id)
    if page:
        q=(db.file.page==page)
    else:
        q=(db.file)
    if db(q).isempty(): #if there are no files related to the page, we select all available files
        q=(db.file)
    files = db(q).select(orderby=~db.file.protected|~db.file.id)

    if not (auth.has_membership('manager') or auth.has_membership('protected_files_access')):
        #restrict protected files for allowed users only
        files = [f for f in files if not f.protected]
    return dict(files=files,
                sizeof_file=sizeof_file,
                manager_toolbar=manager_toolbar)

def files_list():
    manager_toolbar = ManagerToolbar('file')
    files = db(db.file).select(orderby=~db.file.protected|~db.file.id)
    
    if not (auth.has_membership('manager') or auth.has_membership('protected_files_access')):
        #restrict protected files for allowed users only
        files = [f for f in files if not f.protected]
    else:
        #Group all protected files on the same "virtual" page
        for index, f in enumerate(files):
            if f.protected:
                files[index].page = -1
    return dict(files=files,
                sizeof_file=sizeof_file,
                manager_toolbar=manager_toolbar)

@auth.requires_membership('manager')
def edit_file():
    a_file = db.file(request.args(0))
    page = db.page(request.vars.container_id)
    crud.settings.update_deletable=False
    if page:
        db.file.page.default = page.id
    if len(request.args) and a_file:
        crud.settings.update_deletable = False
        form = crud.update(db.file,a_file,next='files_list')
    else:
        form = crud.create(db.file)
    return dict(a_file=a_file, form=form)


@auth.requires_membership('manager')
def delete_file():
    a_file = db.file(request.args(0))
    if len(request.args) and a_file:  
        form = FORM.confirm(T('Yes, I really want to delete this file'),{T('Back'):URL('files_list')})
        if form.accepted:
            #remove the file
            db(db.file.id==a_file.id).delete()
            session.flash = T('File deleted')
            redirect(URL('files_list'))
    return dict(a_file=a_file, form=form)