# -*- coding: utf-8 -*-
# this file is released under public domain and you can use without limitations
#########################################################################
## Customize your APP title, subtitle and menus here
#########################################################################

response.title = request.application
response.subtitle = T('customize me!')

#http://dev.w3.org/html5/markup/meta.name.html
response.meta.author = 'you'
response.meta.description = 'CiSE, IEEE, AIP'
response.meta.keywords = 'CiSE, IEEE, AIP'
response.meta.copyright = 'Copyright 2007-2010'

##########################################
## this is the main application menu
## add/remove items as required
##########################################

response.menu = [
    (T('Home'), False, URL('default','index')),
    (T('For Readers'), False, None, [
            (T('About'),False,'http://computer.org/cse/'),
            (T('Subscribe'),False,'https://www.associationsciences.org/cise/'),
            (T('Alerts'),False,'http://scitation.aip.org/cise/alert.jsp'),            
            ]),
    (T('For Authors'), False, None, [
            (T('Guidelines'),False,'http://computer.org/cse/edguide.htm'),
            (T('Submit an Article'), False, 'http://www.computer.org/portal/web/cise'),
            (T('Calender'),False,'http://www.computer.org/portal/web/computingnow/editorialcalendar'),
            ]),
    (T('For institutions'),False,None, [
            (T('Subscribers'),False,'http://cise.aip.org/journals/doc/CSENFA-home/CiSEInsts11.pdf'),
            ]),
    ]
