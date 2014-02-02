#from gluon.debug import dbg

def show_page():
    """
        Show the requested page
    """
    from gluon.tools import prettydate

    manager_toolbar = ManagerToolbar('page')
    if request.args(0) and request.args(0).isdigit():
        page = db.page(request.args(0))
    else:
        page = db(db.page.url==request.args(0)).select().first()
    #if the page has no content, we select the fisrt child (len < 8 to avoid having a page with just "<br />")
    if page and len(page.content) < 8:
        child = db(db.page.parent==page).select(orderby=db.page.rank|db.page.title).first()
        if child:
            page=child
    if not page:
        if request.args(0) and request.args(0).lower() == 'images':
            redirect(URL('images'))
        else:
            page = db(db.page.is_index==True).select().first()

    disqus_shortname = None
    if page.allow_disqus and WEBSITE_PARAMETERS.disqus_shortname:
        disqus_shortname = WEBSITE_PARAMETERS.disqus_shortname
    pretty_date = prettydate(page.modified_on, T)
    header_component = db.page_component(page.header_component)
    left_sidebar_component = db.page_component(page.left_sidebar_component)
    right_sidebar_component = db.page_component(page.right_sidebar_component)
    left_footer_component = db.page_component(page.left_footer_component)
    middle_footer_component = db.page_component(page.middle_footer_component)
    right_footer_component = db.page_component(page.right_footer_component)
    central_component = db.page_component(page.central_component)
    return dict(page=page,
                header_component=header_component,
                left_sidebar_enabled=page.left_sidebar_enabled,
                right_sidebar_enabled=page.right_sidebar_enabled,
                left_sidebar_component=left_sidebar_component,
                right_sidebar_component=right_sidebar_component,
                left_footer_component=left_footer_component,
                middle_footer_component=middle_footer_component,
                right_footer_component=right_footer_component,
                central_component=central_component,
                manager_toolbar=manager_toolbar,
                pretty_date=pretty_date,
                disqus_shortname=disqus_shortname)

@auth.requires_membership('manager')
def delete_page():
    if request.args(0) and request.args(0).isdigit():
        page = db.page(request.args(0))
    else:
        page = db(db.page.url==request.args(0)).select().first()
    if len(request.args) and page:  
        form = FORM.confirm(T('Yes, I really want to delete this page'),{T('Back'):URL('show_page', args=page.id)})
        if form.accepted:
            #remove images linked to the page
            pathname = path.join(request.folder,'static','images', 'pages_content', str(form.vars.id))
            if path.exists(pathname):
                shutil.rmtree(pathname)
            #remove the page
            db(db.page.id==page.id).delete()
            session.flash = T('Page deleted')
            redirect(URL('default', 'index'))
    return dict(page=page, form=form)

@auth.requires_membership('manager')
def edit_page():
    """
    """

    advanced_fields = ["{}_{}__row".format(db.page, field) for field in 
                            [db.page.rank.name,
                            db.page.url.name,
                            db.page.is_index.name,
                            db.page.is_enabled.name,
                            db.page.header_component.name,
                            db.page.left_sidebar_enabled.name,
                            db.page.right_sidebar_enabled.name,
                            db.page.left_footer_component.name,
                            db.page.middle_footer_component.name,
                            db.page.right_footer_component.name,
                            db.page.central_component.name,
                            db.page.allow_disqus.name,
                            db.page.max_content_height.name]
                        ]
    page_id = request.args(0)
    if page_id:
        if page_id.isdigit():
            page = db.page(page_id)
        else:
            page = db(db.page.url==page_id).select().first()
    if len(request.args) and page:  
        crud.settings.update_deletable = False
        form = crud.update(db.page,page,next=URL('show_page', args=page.id))
        my_extra_element = XML("""
            <div id="wysiwyg_management">
                <ul class="nav nav-pills">
                    <li id="activate_wysiwyg" class="active">
                        <a href="#">%s</a>
                    </li>
                    <li id="remove_wysiwyg" >
                        <a href="#">%s</a>
                    </li>
                </ul>
            </div>
        """ %(T('WYSIWYG view'),T('HTML view')))
        form[0][4].append( my_extra_element)
    else:
        #Hide the "content" of the page : the page has no title
        #and this is impossible to initialise the upload field with page.url
        db.page.content.readable = db.page.content.writable = False
        form = crud.create(db.page,next='edit_page/[id]')
    return dict(form=form, advanced_fields=advanced_fields)
