# -*- coding: utf-8 -*-


###############################################################################
# web2py modelless scaffold app
# Bruno Cezar Rocha <rochacbruno@gmail.com>
#
# default controller
###############################################################################


def index():
    redirect(URL('post', 'index'))


def user():
    from handlers.user import User
    user = User()
    return dict(auth=user.auth, form=user.auth())


def download():
    flnm = request.args(0)
    import os
    response.stream(os.path.join(request.folder, 'uploads', flnm))
