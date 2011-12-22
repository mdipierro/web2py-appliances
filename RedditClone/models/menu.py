# -*- coding: utf-8 -*-
# this file is released under public domain and you can use without limitations
#########################################################################
## Customize your APP title, subtitle and menus here
#########################################################################

categories = db(db.category).select(orderby=db.category.name,cache=(cache.ram,60))
response.menu = [(c.name,False,URL('news',args=c.id)) for c in categories]
