import gluon.fileutils

if not gluon.fileutils.check_credentials(request): redirect('/admin')

def index():
    return dict(sites=db().select(db.web_site.ALL))

def probe():
    import urllib
    try:
        url=db(db.web_site.id==request.args[0]).select()[0].url
        urllib.urlopen(url).read()
        return '<span style="color:green;">Pass</span>'
    except:
        db.failure.insert(url=url)
        return '<span style="color:red;">Fail</span>'
