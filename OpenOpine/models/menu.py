# -*- coding: utf-8 -*-
#########################################################################
##Written by C. S. Schroeder, A Theory of Publishing
##Copyright (C) 2011 Equimind Financial LLC.
##
##Permission is hereby granted, free of charge, to any
##person obtaining a copy of this software and associated
##documentation files (the "Software"), to deal in the
##Software without restriction, including without limitation
##the rights to use, copy, modify, merge, publish,
##distribute, sublicense, and/or sell copies of the
##Software, and to permit persons to whom the Software is
##furnished to do so, subject to the following conditions:
##
##The above copyright notice and this permission notice
##shall be included in all copies or substantial portions of
##the Software.
##
##THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY
##KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE
##WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR
##PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS
##OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR
##OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR
##OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE
##SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
##
##  Powered by web2py, Thanks Massimo!
#########################################################################

#########################################################################
## Customize your APP title, subtitle and menus here
#########################################################################

response.title = request.application
response.subtitle = T('eat well!')

## read more at http://dev.w3.org/html5/markup/meta.name.html
response.meta.author = 'Casey Schroeder <cs@equi-mind.com>'
response.meta.description = 'application for reviews'
response.meta.keywords = 'web development, finance, analytics'
response.meta.generator = 'Web2py Web Framework'
response.meta.copyright = 'Copyright 2011'

## your http://google.com/analytics id
##response.google_analytics_id = ''

#########################################################################
## this is the main application menu add/remove items as required
#########################################################################

response.menu = [
    (T('OpenOpine'), False, URL('default','index'), [])
    ]

#########################################################################
## provide shortcuts for development. remove in production
#########################################################################

def _():
    # shortcuts
    app = request.application
    ctr = request.controller    
    # useful links to internal admin and appadmin pages
    response.menu+=[(T('Reviewers'),False, URL('default','reviewers'), [])]
    response.menu+=[(T('Profiles'),False, URL('default','profiles', vars=dict(tbl="place")),[])]
    response.menu+=[(T('Reviews'),False, URL('default','reviews',vars=dict(tbl="place")), [])]
    if auth.has_membership('reviewer'):
        response.menu+=[(T('Post Profile'),False, URL('default','create_profile', vars=dict(tbl="place")),
                        [(T('Company'),False, URL('default','create_profile', vars=dict(tbl="region"))),
                        (T('Product'),False, URL('default','create_profile', vars=dict(tbl="place"))),
                        (T('Event'),False, URL('default','create_profile', vars=dict(tbl="event")))
                        ])]
        response.menu+=[(T('Post Review'),False, URL('default','create_review',vars=dict(tbl="place")), 
                        [(T('Company'),False, URL('default','create_review', vars=dict(tbl="region"))),
                        (T('Product'),False, URL('default','create_review', vars=dict(tbl="place"))),
                        (T('Event'),False, URL('default','create_review', vars=dict(tbl="event")))
                        ])]
    if auth.has_membership('admin'):
        response.menu+=[(T('Manage'),False, URL('default','create_contributor'), [])]    
_()
