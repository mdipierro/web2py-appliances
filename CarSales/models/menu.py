# -*- coding: utf-8 -*- 

#########################################################################
## Customize your APP title, subtitle and menus here
#########################################################################

response.title=config['nmsite']
response.subtitle=config['dscsite']
response.meta.author='Bruno'
response.meta.description='Car Store'
response.meta.keywords='Cars, new, used'

##########################################
## this is the main application menu
## add/remove items as required
##########################################

response.menu = [
    (T('Home'), False, URL(request.application,'default','index'), []),
    (T('New'), False, URL(request.application,'default','cars',args='new'), []),
    (T('Used'), False, URL(request.application,'default','cars',args='used'),[])
    ]

##########################################
## this is here to provide shortcuts
## during development. remove in production 
##
## mind that plugins may also affect menu
##########################################
"""
response.menu+=[
    (T('Edit'), False, URL('admin', 'default', 'design/%s' % request.application),
     [
            (T('Controller'), False, 
             URL('admin', 'default', 'edit/%s/controllers/%s.py' \
                     % (request.application,request.controller=='appadmin' and
                        'default' or request.controller))), 
            (T('View'), False, 
             URL('admin', 'default', 'edit/%s/views/%s' \
                     % (request.application,response.view))),
            (T('Layout'), False, 
             URL('admin', 'default', 'edit/%s/views/layout.html' \
                     % request.application)),
            (T('Stylesheet'), False, 
             URL('admin', 'default', 'edit/%s/static/base.css' \
                     % request.application)),
            (T('DB Model'), False, 
             URL('admin', 'default', 'edit/%s/models/db.py' \
                     % request.application)),
            (T('Menu Model'), False, 
             URL('admin', 'default', 'edit/%s/models/menu.py' \
                     % request.application)),
            (T('Database'), False, 
             URL(request.application, 'appadmin', 'index')),
            ]
   ),
  ]
"""
