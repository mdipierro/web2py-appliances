# coding: utf8
from os import path

signature = db.Table(db,'auth_signature',
      Field('created_on','datetime',default=request.now,
            writable=False,readable=False, label=T('Created on')),
        Field('created_by','reference %s' % auth.settings.table_user_name,default=auth.user_id,
            writable=False,readable=False, label=T('Created by')),
        Field('modified_on','datetime',update=request.now,default=request.now,
            writable=False,readable=False, label=T('Modified on')),
      Field('modified_by','reference %s' % auth.settings.table_user_name,
            default=auth.user_id,update=auth.user_id,
            writable=False,readable=False, label=T('Modified by'))
      )

db._common_fields.append(signature) #db._common_fields is a list of fields that should belong to all the tables

db.define_table('website_parameters',
    Field('last_fixture_date', 'date', label=T('Last fixture date')),
    Field('website_name_long', label=T('Website name long')),
    Field('website_name', label=T('Website name')),
    Field('website_title', label=T('Website title')),
    Field('website_subtitle', label=T('Website subtitle')),
    Field('website_url', label=T('Url')),
    Field('force_language', label=T('Force a language (en, it, es, fr, ...)')),
    Field('contact_name', label=T('Contact name')),
    Field('contact_trade_register_number', label=T('Trade register number')),
    Field('contact_address', 'text', label=T('Address')),
    Field('contact_google_maps_plan_url', 'text', label=T('Google maps plan url')),
    Field('contact_telephone', label=T('Telephone')),
    Field('contact_fax', label=T('Fax')),
    Field('contact_mobile', label=T('Mobile')),
    Field('contact_form_email', label=T('Contact form email')),
    Field('contact_form_cc', label=T('Contact form cc')),
    Field('contact_form_bcc', label=T('Contact form cci')),
    Field('booking_form_email', label=T('Booking form email')),
    Field('booking_form_cc', label=T('Booking form cc')),
    Field('booking_form_bcc', label=T('Booking form cci')),
    Field('max_old_news_to_show', 'integer', label=T('How many old news (date < current date) shall we show?')),
    Field('mailserver_url', label=T('Mail server url')),
    Field('mailserver_port', 'integer', label=T('Mail server port')),
    Field('mailserver_sender_mail', label=T('Mail server sender email')),
    Field('mailserver_sender_login', label=T('Mail server sender login')),
    Field('mailserver_sender_pass', label=T('Mail server sender pass')),
    Field('google_analytics_id', label=T('Google analytics id')),
    Field('navbar_inverse', 'boolean', default=True, label=T('Inverse navbar color')),
    Field('with_banner', 'boolean', default=True, label=T('Show a banner')),
    Field('with_specific_banner', 'boolean', label=T('Use the specific banner (include the content of "views\\specificbanner.html")')),
    Field('banner_image_always', label=T('Banner image always shown')),
    Field('banner_image_desktop', label=T('Banner image shown on desktop mode only')),
    Field('banner_image_tablet', label=T('Banner image shown on tablet mode only')),
    Field('banner_image_phone', label=T('Banner image shown on phone mode only')),
    Field('banner_image_background_gradient_from', label=T('Banner image background gradient from')),
    Field('banner_image_background_gradient_to', label=T('Banner image background gradient to')),
    Field('seo_website_title', label=T('SEO : Website title (displayed in <title> tag)')),
    Field('seo_meta_author', label=T('SEO : Meta "author"')),
    Field('seo_meta_description', label=T('SEO : Meta "description"')),
    Field('seo_meta_keywords', label=T('SEO : Meta "keywords"')),
    Field('seo_meta_generator', label=T('SEO : Meta "generator"'))
) 
db.website_parameters.website_url.requires = IS_EMPTY_OR(IS_URL())
db.website_parameters.mailserver_sender_mail.requires = IS_EMPTY_OR(IS_EMAIL())
db.website_parameters.contact_form_email.requires = IS_EMPTY_OR(IS_EMAIL())
db.website_parameters.contact_form_cc.requires = IS_EMPTY_OR(IS_EMAIL())
db.website_parameters.contact_form_bcc.requires = IS_EMPTY_OR(IS_EMAIL())
db.website_parameters.booking_form_email.requires = IS_EMPTY_OR(IS_EMAIL())
db.website_parameters.booking_form_cc.requires = IS_EMPTY_OR(IS_EMAIL())
db.website_parameters.booking_form_bcc.requires = IS_EMPTY_OR(IS_EMAIL())

db.define_table('page_component',
    Field('controller', readable=False, writable=False, default='default', label=T('Component controller')),
    Field('name', unique=True, readable=False, writable=False, label=T('Component name')),
    Field('description', readable=False, writable=False, label=T('Component description')),
    Field('ajax', 'boolean', readable=False, writable=False, default=False, label=T('Component with Ajax')),
    Field('ajax_trap', 'boolean', readable=False, writable=False, default=False, label=T('Component with Ajax trap'))
)

db.define_table('page',
    Field('parent', 'reference page', label=T('Parent')),
    Field('title', unique=True, notnull=True, label=T('Title')),
    Field('rank', 'integer', readable=True, writable=True, default=0, label=T('Rank')),
    Field('subtitle', label=T('Subtitle')),
    Field('url', unique=True, readable=True, writable=True, label=T('Url')),
    Field('content', 'text', label=T('Content')),
    Field('is_index', 'boolean', readable=True, writable=True, default=False, label=T('Is index')),
    Field('is_enabled', 'boolean', readable=True, writable=True, default=True, label=T('Is enabled')),
    Field('left_sidebar_enabled', 'boolean', default=False, label=T('Left sidebar')),
    Field('right_sidebar_enabled', 'boolean', default=False, label=T('Right sidebar')),
    Field('left_sidebar_component', 'reference page_component', label=T('Left sidebar component')),
    Field('right_sidebar_component', 'reference page_component', label=T('Right sidebar component')),
    Field('left_footer_component', 'reference page_component', label=T('Left footer component')),
    Field('middle_footer_component', 'reference page_component', label=T('Middle footer component')),
    Field('right_footer_component', 'reference page_component', label=T('Right footer component')),
    format='%(title)s'
)

db.page.parent.requires = IS_EMPTY_OR(IS_IN_DB(db, db.page.id, '%(title)s', zero=T('<Empty>')))
db.page.left_sidebar_component.requires = IS_EMPTY_OR(IS_IN_DB(db, db.page_component.id, '%(name)s - %(description)s', zero=T('<Empty>')))
db.page.right_sidebar_component.requires = IS_EMPTY_OR(IS_IN_DB(db, db.page_component.id, '%(name)s - %(description)s', zero=T('<Empty>')))
db.page.left_footer_component.requires = IS_EMPTY_OR(IS_IN_DB(db, db.page_component.id, '%(name)s - %(description)s', zero=T('<Empty>')))
db.page.right_footer_component.requires = IS_EMPTY_OR(IS_IN_DB(db, db.page_component.id, '%(name)s - %(description)s', zero=T('<Empty>')))
db.page.middle_footer_component.requires = IS_EMPTY_OR(IS_IN_DB(db, db.page_component.id, '%(name)s - %(description)s', zero=T('<Empty>')))
db.page.url.compute = lambda row: IS_SLUG()(row.title)[0]

pageSelector = HierarchicalSelect(db, db.page, db.page.title, db.page.rank)
db.page.parent.widget = pageSelector.widget

db.define_table('image',
    Field('page', 'reference page', label=T('Page')),
    Field('name', notnull=True, label=T('Name')),
    Field('alt', label=T('Alt')),
    Field('comment', label=T('Comment')),
    Field('file', 'upload', uploadfolder=path.join(
        request.folder,'static','images','photo_gallery'
        ), autodelete=True, label=T('File')),
    Field('thumb', 'text', readable=False, writable=False, label=T('Thumb')),
    Field('show_in_gallery', 'boolean', readable=True, writable=True, default=True, label=T('Show in gallery')),
    Field('show_in_banner', 'boolean', readable=True, writable=True, default=False, label=T('Show in banner')),
    format='%(name)s'
)
db.image.page.requires = IS_EMPTY_OR(IS_IN_DB(db, db.page.id, '%(title)s', zero=T('<Empty>')))
db.image.alt.compute = lambda row: row.name.capitalize()
db.image.page.widget = pageSelector.widget

db.define_table('registered_user',
    Field('first_name', label=T('First name')),
    Field('last_name', label=T('Last name')),
    Field('email', unique=True, requires=[IS_EMAIL(), IS_NOT_IN_DB(db, 'registered_user.email')], label=T('Email')),
    format='%(email)s'
    )

db.define_table('news',
   Field('title', label=T('Title')),
   Field('date','date',default=request.now,label=T('Date')),
   Field('text','text',label=T('News content')),
   Field('published_on', 'datetime', default=request.now),
   format='%(text)s'
   )

db.define_table('file',
   Field('page', 'reference page', label=T('Page')),
   Field('title', label=T('Title'), notnull=True),
   Field('comment', label=T('Comment')),
   Field('file', 'upload', uploadfolder=path.join(
        request.folder,'static','uploaded_files'
        ), notnull=True, autodelete=True, label=T('File')),
   Field('size', 'double', readable=False, writable=False, label=T('Size')),
   format='%(title)s'
   )
db.file.page.requires = IS_EMPTY_OR(IS_IN_DB(db, db.page.id, '%(title)s', zero=T('<Empty>')))
db.file.size.compute = lambda row: path.getsize(path.join(request.folder,'static','uploaded_files',row.file))
db.file.page.widget = pageSelector.widget

## after defining tables, uncomment below to enable auditing
auth.enable_record_versioning(db)