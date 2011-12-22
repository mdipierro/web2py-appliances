#!/usr/bin/python
# -*- coding: utf-8 -*-
import os
try:
    import Image
except ImportError:
    raise HTTP(200,"requires Python Imaging Library")

# # sample index page with internationalization (T)
def index():
    response.flash = T('Welcome to web2py')
    statement = "test"
    form=FORM(TABLE(TR("Statement",INPUT(_type="text",_name="statement",requires=IS_NOT_EMPTY())),
                    TR("",INPUT(_type="submit",_value="SUBMIT"))))

    if form.accepts(request,session):
        response.flash="Picture Created"
        statement = form.vars.statement

    path = '/usr/bin/iec16022'
    params = '-f PNG -c "%s" -o ./applications/semaPrinter/static/semacode/semacode1.png' % statement
    totalCommand = (path+" "+ params)
    os.system(totalCommand)

    #Get the width and height of the image...
    semaSize = Image.open('./applications/semaPrinter/static/semacode/semacode1.png').size
    

    return dict(form=form, vars=form.vars, semaSize=semaSize)


# # uncomment the following if you have defined "auth" and "crud" in models
# def user(): return dict(form=auth())
# def data(): return dict(form=crud())
# def download(): return response.download(request,db)
# # tip: use @auth.requires_login, requires_membership, requires_permission
