from gluon.contenttype import contenttype
import os

def index():
    shows=db().select(db.show.ALL,orderby=db.show.name)
    return dict(shows=shows)


def show():
    try:
        show_id=int(request.args[0])
        title=db(db.show.id==show_id).select(db.show.name)[0].name
    except: redirect(URL('index'))
    images=db(db.image.show==show_id).select()
    return dict(title=title,images=images)


def download():
    filename=request.args[0]
    response.headers['Content-Type']=contenttype(filename)
    return open(os.path.join(request.folder,'uploads/','%s' % filename),'rb').read()
