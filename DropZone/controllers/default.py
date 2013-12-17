# -*- coding: utf-8 -*-
#########################################################################
## Author: Leonel Câmara
## File is released under public domain and you can use without limitations
#########################################################################

def index():
    """ Deal with submitted files in the dropzone """
    from gluon.utils import web2py_uuid
    from datetime import timedelta

    form = SQLFORM(db.testfile, formstyle='divs')
    response.flash = 'please fill out the form'
    # Some attempts to protect against CSRF
    if request.env.http_referer is not None:
        # Check referrer, it sort of helps.
        from urlparse import urlparse
        if urlparse(request.env.http_referer).netloc != request.env.http_host:
            raise HTTP(403)
    if not session.dz_token:
        # Emit a token we can demand during file submission
        session.dz_token = web2py_uuid()
        session.dz_token_validity = request.utcnow + timedelta(minutes=20)
    elif request.utcnow > session.dz_token_validity:
        del session.dz_token
        del session.dz_token_validity
        redirect(URL(), client_side=True)
    else:
        # We are forcing each user to only have 1 file with each filename as we're
        # using it to find specific files.
        if 'image' in request.vars:
            request.vars.name = db.testfile.name.default = response.session_id +'___' + request.vars.image.filename

        # If everything looks fine with the token, process the form.
        if request.env.http_x_dz_token == session.dz_token or request.vars._formkey == session.dz_token: 
            if form.accepts(request.vars, session=None, formname=None):
                response.flash = response.flash = T('File Accepted')
                # One could extend token validity here
                session.dz_token_validity = request.utcnow + timedelta(minutes=20)
            elif form.errors:
                # Send the first error as the text
                response.flash = form.errors.items()[0][1]
                if request.env.http_x_dz_token:  # if we have the header we're being called by ajax
                    raise HTTP(406, form.errors.items()[0][1])  # Not Acceptable

    files = db(db.testfile.name.startswith(response.session_id)).select()
    return {'form': form, 'files': files}


def remove():
    """ Remove a recently posted file """
    if not session.dz_token or (request.env.http_x_dz_token != session.dz_token) or (request.utcnow > session.dz_token_validity):
        raise HTTP(403)  # Forbidden GTFO
    db(db.testfile.name == '%s___%s' % (response.session_id, request.vars.filename)).delete()
    response.flash = T('File Deleted')


@cache.action()
def download():
    """
    allows downloading of uploaded files
    http://..../[app]/default/download/[filename]
    """
    return response.download(request, db)


