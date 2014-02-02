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

db.define_table('contact',
    Field('name', label=T('Contact name')),
    Field('trade_register_number', label=T('Trade register number')),
    Field('description', 'text', label=T('Description')),
    Field('address', 'text', label=T('Address')),
    Field('google_maps_plan_url', 'text', label=T('Google maps plan url')),
    Field('telephone', label=T('Telephone')),
    Field('fax', label=T('Fax')),
    Field('mobile', label=T('Mobile')),
    Field('website', label=T('Website')),
    Field('email', label=T('Email')),
    Field('contact_form_email', label=T('Contact form email')),
    Field('contact_form_cc', label=T('Contact form cc')),
    Field('contact_form_bcc', label=T('Contact form cci')),
    Field('show_in_address_component', 'boolean', default=True, label=T('Show in address component')),
    Field('show_in_contact_form', 'boolean', default=True, label=T('Show in contact form'))
)
db.contact.website.requires = IS_EMPTY_OR(IS_URL())
db.contact.email.requires = IS_EMPTY_OR(IS_EMAIL())
db.contact.contact_form_email.requires = IS_EMPTY_OR(IS_EMAIL())
db.contact.contact_form_cc.requires = IS_EMPTY_OR(IS_EMAIL())
db.contact.contact_form_bcc.requires = IS_EMPTY_OR(IS_EMAIL())

db.define_table('website_parameters',
    Field('last_fixture_date', 'date', label=T('Last fixture date'), comment=T('When last_fixture_date < current date, we apply the fixtures (see models/x_fixtures.py)')),
    Field('website_name_long', label=T('Website name long'), comment=T('Shown in the banner footer')),
    Field('website_name', label=T('Website name'), comment=T('Shown in top left logo')),
    Field('website_title', label=T('Website title'), comment=T('Displayed instead of the banner if "with_banner"=False')),
    Field('website_subtitle', label=T('Website subtitle'), comment=T('Shown in the banner footer')),
    Field('website_url', label=T('Url'), comment=T('URL of the website')),
    Field('force_language', label=T('Force a language (en, it, es, fr, ...)')),
    Field('booking_form_email', label=T('Booking form email'), comment=T('Messages of the booking form will be sent to this email')),
    Field('booking_form_cc', label=T('Booking form cc'), comment=T('Messages of the booking form will be cc to this email')),
    Field('booking_form_bcc', label=T('Booking form cci'), comment=T('Messages of the booking form will be cci to this email')),
    Field('max_old_news_to_show', 'integer',label=T('Max number of old news'), comment=T('How many old news (date < current date) shall we show?')),
    Field('max_gallery_images_to_show', 'integer',label=T('Max number of images in gallery'), comment=T('How many maximum images shall we show in photo gallery?')),
    Field('mailserver_url', label=T('Mail server url'), comment=T('URL of the mailserver (used to send email in forms)')),
    Field('mailserver_port', 'integer', label=T('Mail server port'), comment=T('Port of the mailserver (used to send email in forms)')),
    Field('mailserver_sender_mail', label=T('Mail server sender email'), comment=T('Sender email adress of the mailserver (used to send email in forms)')),
    Field('mailserver_sender_login', label=T('Mail server sender login'), comment=T('Login of the mailserver (used to send email in forms)')),
    Field('mailserver_sender_pass', label=T('Mail server sender pass'), comment=T('Pass of the mailserver (used to send email in forms)')),
    Field('google_analytics_id', label=T('Google analytics id'), comment=T('Your Google Analytics account ID')),
    Field('navbar_inverse', 'boolean', default=True, label=T('Inverse navbar color')),
    Field('with_banner', 'boolean', default=True, label=T('Show a banner'), comment=T('If False, we display website_title instead')),
    Field('with_specific_banner', 'boolean', label=T('Use the specific banner'), comment=T('Include the content of "views/specificbanner.html"')),
    Field('add_website_name_as_logo', 'boolean', label=T('Add the website name as a logo'), comment=T('Will be displayed at the top left corner')),
    Field('custom_bootstrap_css_file', label=T('Name of the custom bootstrap CSS file')),
    Field('banner_image_always', label=T('Banner image always shown'), comment=T('URI of the image which will be always shown in the banner')),
    Field('banner_image_desktop', label=T('Banner image shown on desktop mode'), comment=T('URI of the image which will be shown in the banner on desktop mode onlw')),
    Field('banner_image_tablet', label=T('Banner image shown on tablet mode'), comment=T('URI of the image which will be shown in the banner on tablet mode only')),
    Field('banner_image_phone', label=T('Banner image shown on phone mode'), comment=T('URI of the image which will be shown in the banner on phone mode only')),
    Field('banner_image_background_gradient_from', label=T('Banner image background gradient from'), comment=T('Start color to display a gradient behind banner image')),
    Field('banner_image_background_gradient_to', label=T('Banner image background gradient to'), comment=T('End color to display a gradient behind banner image')),
    Field('seo_website_title', label=T('SEO : Website title'), comment=T('Displayed in <title> tag of the HTML source code')),
    Field('seo_meta_author', label=T('SEO : Meta "author"'), comment=T('Displayed in <meta author> tag of the HTML source code')),
    Field('seo_meta_description', label=T('SEO : Meta "description"'), comment=T('Displayed in <meta description> tag of the HTML source code')),
    Field('seo_meta_keywords', label=T('SEO : Meta "keywords"'), comment=T('Displayed in <meta keywords> tag of the HTML source code')),
    Field('seo_meta_generator', label=T('SEO : Meta "generator"'), comment=T('Displayed in <meta generator> tag of the HTML source code')),
    Field('show_booking_menu', 'boolean', default=True, label=T('Show booking menu'), comment=T('Show the booking menu (to manage booking requests)')),
    Field('show_event_menu', 'boolean', default=True, label=T('Show event menu'), comment=T('Show the event menu (to manage events on a calendar)')),
    Field('disqus_shortname', default=True, label=T('Disqus shortname'), comment=T('Add here your disqus shortname to activate comments on your pages. Note : you need to fill "website_url" too!'))
) 
db.website_parameters.website_url.requires = IS_EMPTY_OR(IS_URL())
db.website_parameters.mailserver_sender_mail.requires = IS_EMPTY_OR(IS_EMAIL())
db.website_parameters.booking_form_email.requires = IS_EMPTY_OR(IS_EMAIL())
db.website_parameters.booking_form_cc.requires = IS_EMPTY_OR(IS_EMAIL())
db.website_parameters.booking_form_bcc.requires = IS_EMPTY_OR(IS_EMAIL())

db.define_table('page_component',
    Field('controller', readable=False, writable=False, default='default', label=T('Component controller')),
    Field('name', unique=False, readable=False, writable=False, label=T('Component name')),
    Field('description', readable=False, writable=False, label=T('Component description')),
    Field('ajax', 'boolean', readable=False, writable=False, default=False, label=T('Component with Ajax')),
    Field('ajax_trap', 'boolean', readable=False, writable=False, default=False, label=T('Component with Ajax trap')),
    Field('container_class', readable=False, writable=False, label=T('Class of the container'), comment=T('For example "hidden-phone"')),
    Field('parent', 'reference page_component', label=T('Parent')),
    Field('rank', 'integer', readable=True, writable=True, default=0, label=T('Rank')),
)
db.page_component.parent.requires = IS_EMPTY_OR(IS_IN_DB(db, db.page_component.id, '%(description)s', zero=T('<Empty>')))

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
    Field('header_component', 'reference page_component', label=T('Header component')),
    Field('left_sidebar_component', 'reference page_component', label=T('Left sidebar component')),
    Field('right_sidebar_component', 'reference page_component', label=T('Right sidebar component')),
    Field('left_footer_component', 'reference page_component', label=T('Left footer component')),
    Field('middle_footer_component', 'reference page_component', label=T('Middle footer component')),
    Field('right_footer_component', 'reference page_component', label=T('Right footer component')),
    Field('central_component', 'reference page_component', label=T('Central component')),
    Field('allow_disqus', 'boolean', label=T('Allow disqus (must be configured in website_parameters)')),
    Field('max_content_height', 'integer', readable=True, writable=True, default=0, label=T('Max height (in pixels) of the page content (0 = no max height)')),
    format='%(title)s'
)

db.page.parent.requires = IS_EMPTY_OR(IS_IN_DB(db, db.page.id, '%(title)s', zero=T('<Empty>')))
db.page.header_component.requires = IS_EMPTY_OR(IS_IN_DB(db, db.page_component.id, '%(name)s - %(description)s', zero=T('<Empty>')))
db.page.left_sidebar_component.requires = IS_EMPTY_OR(IS_IN_DB(db, db.page_component.id, '%(name)s - %(description)s', zero=T('<Empty>')))
db.page.right_sidebar_component.requires = IS_EMPTY_OR(IS_IN_DB(db, db.page_component.id, '%(name)s - %(description)s', zero=T('<Empty>')))
db.page.left_footer_component.requires = IS_EMPTY_OR(IS_IN_DB(db, db.page_component.id, '%(name)s - %(description)s', zero=T('<Empty>')))
db.page.right_footer_component.requires = IS_EMPTY_OR(IS_IN_DB(db, db.page_component.id, '%(name)s - %(description)s', zero=T('<Empty>')))
db.page.middle_footer_component.requires = IS_EMPTY_OR(IS_IN_DB(db, db.page_component.id, '%(name)s - %(description)s', zero=T('<Empty>')))
db.page.central_component.requires = IS_EMPTY_OR(IS_IN_DB(db, db.page_component.id, '%(name)s - %(description)s', zero=T('<Empty>')))
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
#db.image.page.widget = pageSelector.widget

db.define_table('registered_user',
    Field('first_name', label=T('First name')),
    Field('last_name', label=T('Last name')),
    Field('email', unique=True, requires=[IS_EMAIL(), IS_NOT_IN_DB(db, 'registered_user.email')], label=T('Email')),
    Field('subscribe_to_newsletter', 'boolean', default=True, label=T("User want to receive newsletter emails")),
    format='%(email)s'
    )

db.define_table('news',
   Field('title', label=T('Title')),
   Field('date','date',default=request.now,label=T('Date')),
   Field('text','text',label=T('News content')),
   Field('published_on', 'datetime', default=request.now),
   Field('send_mail', 'boolean', readable=True, writable=True, default=False, label=T('Send an email to the registered users to inform them')),
   Field('mail_sent', 'boolean', readable=False, writable=False, default=False, label=T('An email has been send to the registered users')),
   Field('max_content_height', 'integer', readable=True, writable=True, default=0, label=T('Max height (in pixels) of the news content (0 = no max height)')),
   format='%(text)s'
   )

db.define_table('file',
   Field('page', 'reference page', label=T('Page')),
   Field('title', label=T('Title'), notnull=True),
   Field('comment', label=T('Comment')),
   Field('file', 'upload', uploadfolder=path.join(
        request.folder,'static','uploaded_files'
        ), notnull=True, autodelete=True, label=T('File')),
   Field('protected', 'boolean', readable=True, writable=True, default=False, label=T('Protected (visible only for authorized users)')),
   Field('size', 'double', readable=False, writable=False, label=T('Size')),
   format='%(title)s'
   )
db.file.page.requires = IS_EMPTY_OR(IS_IN_DB(db, db.page.id, '%(title)s', zero=T('<Empty>')))
db.file.size.compute = lambda row: path.getsize(path.join(request.folder,'static','uploaded_files',row.file))
#db.file.page.widget = pageSelector.widget

## after defining tables, uncomment below to enable auditing
auth.enable_record_versioning(db)