def index():
    return dict()

def user():
    auth.settings.login_next = URL('news','index')
    return dict(form=auth())
