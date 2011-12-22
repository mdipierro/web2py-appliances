session.forget() # comment or remove if you want to store sessions

def index():
    redirect(URL('test'))
    

def test():
    return dict()
