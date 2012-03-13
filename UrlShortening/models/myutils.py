from urllib import urlopen

def thumbalizr(url):
    """ free service to download web page thumbnail """ 
    stream = urlopen('http://api1.thumbalizr.com/?url=%s&width=250' % url)
    return Link.screenshot.store(stream,filename='image.png')

def wotrate(url):
    """ Web Of Trust service for web site rating """
    from gluon.contrib.simplejson import loads
    wot = 'http://api.mywot.com/0.4/public_link_json?hosts=%s/'
    url = url.split('/')[2]
    return loads(urlopen(wot % url).read())[url]
