
response.menu = [('Home',0,URL('index'))]

# allows to browser, search, and upload new music (if logged in)                
def index():
    # tell web2py that links to music files are to be                           
    # represented as HTML5 audio embedded players                               
    from gluon.contrib.autolinks import expand_one
    db.music.filename.represent = lambda v,r:         XML(expand_one(URL('download',args=v),{}))
    return dict(grid = SQLFORM.grid(db.music))

# perform login/logout/registration/etc.                                        
def user():
    return dict(form=auth())

# allow streaming of all files, including partial content of music files        
@cache.action()
def download():
    return response.download(request, db)

