# -*- coding: utf-8 -*-

# from gluon.debug import dbg

@auth.requires_membership('manager')
def settings():
    website_parameters = db(db.website_parameters).select().first()
    form = crud.update(db.website_parameters,website_parameters)
    return dict(form=form)

def index():
    #Check if WEBSITE_PARAMETERS initialised. If not, we can either start with dummy data, or a blank database
    if not WEBSITE_PARAMETERS:
        form = FORM.confirm(T('I want to start with an empty database'),{T('I want to try the example database'):URL('populate_example_database')})
        if form.accepted:
            redirect(URL('default','create_empty_database'))
        return dict(form=form)
    page = db(db.page.is_index==True).select().first()
    if not page:
        raise HTTP(404, T('sorry, the page you requested does not exist'))
    redirect(URL('pages','show_page',args=page.url))
    
def create_empty_database():
    form = SQLFORM(db.website_parameters)
    if form.process().accepted:
        if db(db.page.is_index == True).count() == 0:
            db.page.insert(
                title='Index',
                subtitle='The index page',
                url='index',
                content='Empty database created. If you want, you can now remove *.tiny_demo files in your app folder',
                is_index=True,
                left_sidebar_enabled=False,
                right_sidebar_enabled=False
            )
        redirect(URL('index'))
    elif form.errors:
       response.flash = T('form has errors')
    return dict(form=form)
    
def populate_example_database():
    from os import rename

    fixtures_path = path.join(request.folder,'models')
    banner_image_path = path.join(request.folder,'static', 'images', 'banner')
    photo_gallery_path = path.join(request.folder,'static', 'images', 'photo_gallery')
    photo_gallery_thumb_path = path.join(request.folder,'static', 'images', 'photo_gallery', 'thumbs')
    uploaded_files_path = path.join(request.folder,'static', 'uploaded_files')

    if request.args(0):
        #rename x_fixtures.bak in x_fixtures.py to avoid populate the database in the future
        if path.exists(path.join(fixtures_path,'x_fixtures.py')):
            rename(path.join(fixtures_path,'x_fixtures.py'),path.join(fixtures_path,'x_fixtures.tiny_demo'))
        redirect(URL('index'))
    #rename x_fixtures.bak in x_fixtures.py to populate the database
    if path.exists(path.join(fixtures_path,'x_fixtures.tiny_demo')):
        rename(path.join(fixtures_path,'x_fixtures.tiny_demo'),path.join(fixtures_path,'x_fixtures.py'))
    #activate the demo banner
    if path.exists(path.join(banner_image_path,'banner.tiny_demo')):
        rename(path.join(banner_image_path,'banner.tiny_demo'),path.join(banner_image_path,'banner.jpg'))
    #activate photo gallery images
    for i in range(1,7):
        if path.exists(path.join(photo_gallery_path,'demo%d.tiny_demo' %i)):
            rename(path.join(photo_gallery_path,'demo%d.tiny_demo' %i),path.join(photo_gallery_path,'demo%d.jpg' %i))
    #activate photo gallery thumb images
    for i in range(1,7):
        if path.exists(path.join(photo_gallery_thumb_path,'demo%d.tiny_demo' %i)):        
            rename(path.join(photo_gallery_thumb_path,'demo%d.tiny_demo' %i),path.join(photo_gallery_thumb_path,'demo%d.jpg' %i))
    redirect(URL(populate_example_database,args=True))

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
    return response.download(request, db)

def address():
    """
    Allows to access the "address" component
    """
    contacts = db(db.contact.show_in_address_component == True).select()
    return dict(contacts=contacts)

def newsletter():
    """
    Allows to access the "newsletter" component
    """
    db.registered_user.subscribe_to_newsletter.readable = db.registered_user.subscribe_to_newsletter.writable = False
    form = SQLFORM(db.registered_user, _class='blueText')
    if form.process().accepted:
       response.flash = T('form accepted')
    elif form.errors:
       response.flash = T('form has errors')
    return dict(form=form)


def meta_component():
    """
    Allows to access the "meta_component" component
    """
    components = db(db.page_component.parent == request.vars.component_id).select(orderby = db.page_component.rank)
    page = db.page(request.vars.container_id)
    return dict(page=page, components=components)

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

def contact_form():
    """
    Contact form
    """
    from gluon.tools import Recaptcha

    public_key = '6LfBX90SAAAAAKZn2zPK5i72PZsnm9Ouj6BC67k7'
    private_key = '6LfBX90SAAAAADRYFTj5xMyZnZoWycdkCBlF_Djb '
    
    form=SQLFORM.factory(
        Field('your_name',requires=IS_NOT_EMPTY(), label=T('Your name')),
        Field('your_email',requires=IS_EMAIL(), label=T('Your email')),
        Field('subject',requires=IS_NOT_EMPTY(), label=T('Subject')),
        Field('message', 'text',requires=IS_NOT_EMPTY(), label=T('Message'))
        )

    contacts = db(db.contact.show_in_contact_form == True).select()
    opt=[OPTION(contact.name, _value=contact.id) for contact in contacts]
    sel = SELECT(opt,_id="%s_%s" % ('no_table', 'send_to'),
                            _class='generic-widget', 
                            _name='send_to'
                        )
    my_extra_element = TR(TD(LABEL(T('Send to')),_class='w2p_fl'),TD(sel,_class='w2p_fw'), _id="no_table_send_to__row")
    form[0].insert(-2,my_extra_element)
    nb_contact=len(contacts)
    ## Uncomment here to add the captcha...
    #form.element('table').insert(-1,(T('Confirm that you are not a machine'),Recaptcha(request, public_key, private_key),''))

    if form.process().accepted:
        a_contact = db.contact(form.vars.send_to)
        if nb_contact > 1:
            mail_subject = T('Question from %s for %s on %s website') % (form.vars.your_name,a_contact.name,WEBSITE_PARAMETERS.website_name)
        else:
            mail_subject = T('Question from %s on %s website') % (form.vars.your_name,WEBSITE_PARAMETERS.website_name)
        if a_contact:
            message=T("""
                Name : %s
                Email : %s
                Subject : %s
                Message : %s
            """) % (form.vars.your_name, form.vars.your_email, form.vars.subject, form.vars.message)
            if mail:
                if mail.send(
                            to=a_contact.contact_form_email,
                            cc=a_contact.contact_form_cc if a_contact.contact_form_cc else '',
                            bcc=a_contact.contact_form_bcc if a_contact.contact_form_bcc else '',
                            subject=mail_subject,
                            reply_to = form.vars.your_email,
                            message = message):
                    response.flash = T('Your message has been sent. Thank you')
                    response.js = "jQuery('#%s').hide()" % request.cid
                else:
                    response.flash = T('Unable to send the email')
            else:
                response.flash = T('Unable to send the email : email parameters not defined')
        else:
            response.flash = T('Unable to send the email : no contact selected')
    return dict(form=form,
                nb_contact=nb_contact,
                left_sidebar_enabled=True,
                right_sidebar_enabled=True)

# def sitemap():
#     # Import Regex
#     from gluon.myregex import regex_expose
     
#     # Finding You Controllers
#     ctldir = path.join(request.folder,"controllers")
#     ctls=os.listdir(ctldir)
#     # Excluding The appadmin.py and the Manage.py
#     if 'appadmin.py' in ctls: ctls.remove('appadmin.py')
#     if 'manage.py' in ctls: ctls.remove('manage.py')
     
#     # Adding Schemas for the site map
#     xmlns='xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"\n'
#     xmlnsImg='xmlns:image="http://www.google.com/schemas/sitemap-image/1.1"\n'
#     xmlnsVid='xmlns:video="http://www.google.com/schemas/sitemap-video/1.1"\n'
#     sitemap_xml = '<?xml version="1.0" encoding="UTF-8"?>\n'
#     sitemap_xml +='<urlset %s %s %s>\n'%(xmlns,xmlnsImg,xmlnsVid)
     
#     # Add The Pages That You Dont want in the XML Sitemap
#     ExcludedPages = ['Function_Name']
     
#     # Define Your Domain
#     Domain = WEBSITE_PARAMETERS.website_url
     
#     for ctl in ctls:
#         if ctl.endswith(".bak") == False:
#             filename = path.join(ctldir,ctl)
#             data = open(filename, 'r').read()
#             functions = regex_expose.findall(data)
#             ctl = ctl[:-3].replace("_"," ")
             
#             # Adding Statics URLs From Your Controllers
#             for f in functions:
#                 # Ignore the Pages from the list above ( ExcludedPages )
#                 if f not in ExcludedPages:
#                     sitemap_xml += '<url>\n<loc>%s/%s/%s</loc>\n</url>\n' %(Domain,ctl,f.replace("_"," "))
     
#     # Dynamic URLs From Tables For ex ... >> www.domain.com/post/1
#     pages = db().select(db.page.ALL)
#     for page in pages:
#         sitemap_xml += '<url>\n<loc>%s/default/show_page/%s</loc>\n</url>\n' %(Domain,page.url)
#     sitemap_xml +='</urlset>'
#     return sitemap_xml
