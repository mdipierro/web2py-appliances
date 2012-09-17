# -*- coding: utf-8 -*-
# this file is released under public domain and you can use without limitations

#########################################################################
## Customize your APP title, subtitle and menus here
#########################################################################

response.title = ' '.join(word.capitalize() for word in request.application.split('_'))
response.subtitle = T('Stock Forms for Web2py')

## read more at http://dev.w3.org/html5/markup/meta.name.html
response.meta.author = 'Joe Codeswell <joecodeswell@gmail.com>'
response.meta.description = 'Stock Forms for Web2py'
response.meta.keywords = 'web2py, python, framework'
response.meta.generator = 'Web2py Web Framework'

## your http://google.com/analytics id
response.google_analytics_id = None

#########################################################################
## this is the main application menu add/remove items as required
#########################################################################

response.menu = [
    (T('Home'), False, URL('default','index'), []),
	(T('ContactUs'), False, URL('default','index'), [
		(T('CU-00'), False, URL('default','update_t_contactus00'), []),
		(T('CU-01'), False, URL('default','update_t_contactus01'), []),
		(T('CU-02'), False, URL('default','update_t_contactus02'), []),
		(T('CU-03'), False, URL('default','update_t_contactus03'), []),
		(T('CU-04'), False, URL('default','update_t_contactus04'), []),
	]),
	(T('SignUp'), False, URL('default','index'), [
		(T('SU-00'), False, URL('default','update_t_signup00'), []),
		(T('SU-01'), False, URL('default','update_t_signup01'), []),
		(T('SU-02'), False, URL('default','update_t_signup02'), []),
		(T('SU-03'), False, URL('default','update_t_signup03'), []),
		(T('SU-04'), False, URL('default','update_t_signup04'), []),
	]),
	(T('Appointment'), False, URL('default','index'), [
		(T('APP-00'), False, URL('default','update_t_appointment00'), []),
		(T('APP-01'), False, URL('default','update_t_appointment01'), []),
		(T('APP-02'), False, URL('default','update_t_appointment02'), []),
		(T('APP-03'), False, URL('default','update_t_appointment03'), []),
	]),
    ]

#########################################################################
## provide shortcuts for development. remove in production
#########################################################################
'''
def _():
    # shortcuts
    app = request.application
    ctr = request.controller
    # useful links to internal and external resources
    response.menu+=[
        (SPAN('web2py',_style='color:yellow'),False, 'http://web2py.com', [
                (T('My Sites'),False,URL('admin','default','site')),
                (T('This App'),False,URL('admin','default','design/%s' % app), [
                        (T('Controller'),False,
                         URL('admin','default','edit/%s/controllers/%s.py' % (app,ctr))),
                        (T('View'),False,
                         URL('admin','default','edit/%s/views/%s' % (app,response.view))),
                        (T('Layout'),False,
                         URL('admin','default','edit/%s/views/layout.html' % app)),
                        (T('Stylesheet'),False,
                         URL('admin','default','edit/%s/static/css/web2py.css' % app)),
                        (T('DB Model'),False,
                         URL('admin','default','edit/%s/models/db.py' % app)),
                        (T('Menu Model'),False,
                         URL('admin','default','edit/%s/models/menu.py' % app)),
                        (T('Database'),False, URL(app,'appadmin','index')),
                        (T('Errors'),False, URL('admin','default','errors/' + app)),
                        (T('About'),False, URL('admin','default','about/' + app)),
                        ]),
                ('web2py.com',False,'http://www.web2py.com', [
                        (T('Download'),False,'http://www.web2py.com/examples/default/download'),
                        (T('Support'),False,'http://www.web2py.com/examples/default/support'),
                        (T('Demo'),False,'http://web2py.com/demo_admin'),
                        (T('Quick Examples'),False,'http://web2py.com/examples/default/examples'),
                        (T('FAQ'),False,'http://web2py.com/AlterEgo'),
                        (T('Videos'),False,'http://www.web2py.com/examples/default/videos/'),
                        (T('Free Applications'),False,'http://web2py.com/appliances'),
                        (T('Plugins'),False,'http://web2py.com/plugins'),
                        (T('Layouts'),False,'http://web2py.com/layouts'),
                        (T('Recipes'),False,'http://web2pyslices.com/'),
                        (T('Semantic'),False,'http://web2py.com/semantic'),
                        ]),
                (T('Documentation'),False,'http://www.web2py.com/book', [
                        (T('Preface'),False,'http://www.web2py.com/book/default/chapter/00'),
                        (T('Introduction'),False,'http://www.web2py.com/book/default/chapter/01'),
                        (T('Python'),False,'http://www.web2py.com/book/default/chapter/02'),
                        (T('Overview'),False,'http://www.web2py.com/book/default/chapter/03'),
                        (T('The Core'),False,'http://www.web2py.com/book/default/chapter/04'),
                        (T('The Views'),False,'http://www.web2py.com/book/default/chapter/05'),
                        (T('Database'),False,'http://www.web2py.com/book/default/chapter/06'),
                        (T('Forms and Validators'),False,'http://www.web2py.com/book/default/chapter/07'),
                        (T('Email and SMS'),False,'http://www.web2py.com/book/default/chapter/08'),
                        (T('Access Control'),False,'http://www.web2py.com/book/default/chapter/09'),
                        (T('Services'),False,'http://www.web2py.com/book/default/chapter/10'),
                        (T('Ajax Recipes'),False,'http://www.web2py.com/book/default/chapter/11'),
                        (T('Components and Plugins'),False,'http://www.web2py.com/book/default/chapter/12'),
                        (T('Deployment Recipes'),False,'http://www.web2py.com/book/default/chapter/13'),
                        (T('Other Recipes'),False,'http://www.web2py.com/book/default/chapter/14'),
                        (T('Buy this book'),False,'http://stores.lulu.com/web2py'),
                        ]),
                (T('Community'),False, None, [
                        (T('Groups'),False,'http://www.web2py.com/examples/default/usergroups'),
                        (T('Twitter'),False,'http://twitter.com/web2py'),
                        (T('Live Chat'),False,'http://webchat.freenode.net/?channels=web2py'),
                        ]),
                (T('Plugins'),False,None, [
                        ('plugin_wiki',False,'http://web2py.com/examples/default/download'),
                        (T('Other Plugins'),False,'http://web2py.com/plugins'),
                        (T('Layout Plugins'),False,'http://web2py.com/layouts'),
                        ])
                ]
         )]
_()

'''