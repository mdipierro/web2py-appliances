# -*- coding: utf-8 -*-
from plugin_color_widget import color_widget

db = DAL('sqlite:memory:')
db.define_table('product', Field('color', widget=color_widget))

################################ The core ######################################
# Iinject the color widget
db.product.color.widget = color_widget
################################################################################

def index():
    form = SQLFORM(db.product)
    if form.accepts(request, session):
        session.flash = 'submitted %s' % form.vars
        redirect(URL('index'))
    return dict(form=form)
