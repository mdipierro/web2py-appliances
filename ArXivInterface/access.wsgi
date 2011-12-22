# in httpd.conf:
#
# <VirtualHost *:80>
#   WSGIDaemonProcess web2py user=qcd group=qcd
#   WSGIProcessGroup web2py
#   ServerAdmin webmaster@qcd.nersc.gov
#   DocumentRoot /project/projectdirs/qcd/www
#   ServerName qcd.nersc.gov
#   ErrorLog logs/qcd-error_log
#   CustomLog logs/qcd-access_log common
#
#   ScriptAlias /bin/ "/project/projectdirs/qcd/cgi-bin/"
#   <Directory "/project/projectdirs/qcd/cgi-bin">
#     WSGIAccessScript  /project/projectdirs/qcd/access.wsgi
#   </Directory>
# </VirtualHost>

URL_CHECK_ACCESS = 'http://qcd.nersc.gov:9080/nersc/default/check_access'

def allow_access(environ,host):
    import os
    import urllib
    import urllib2
    import datetime
    header = '%s @ %s ' % (datetime.datetime.now(),host) + '='*20
    pprint = '\n'.join('%s:%s' % item for item in environ.items())
    filename = os.path.join(os.path.dirname(__file__),'access.wsgi.log')
    f = None
    try:
        f = open(filename,'a')
	f.write('\n'+header+'\n'+pprint+'\n')
    finally:
    	if f: f.close()
    app = 'nersc' # environ['REQUEST_URI'].split('/')[1]
    keys = [key for key in environ if key.startswith('HTTP_')]
    headers = {}
    for key in environ:
        if key.startswith('HTTP_'):
            headers[key[5:]] = environ[key]
    try:
        data = urllib.urlencode({'request_uri':environ['REQUEST_URI']})
        request = urllib2.Request(URL_CHECK_ACCESS % dict(app=app),
                                  data,headers)
	response = urllib2.urlopen(request).read().strip().lower()
	if response.startswith('true'):
            return True
    except:
        pass
    return False
