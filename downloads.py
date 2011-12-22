import re
import urllib
import os

d = {}
for i in range(1,100):
    try:
        print i,'...'
        page = urllib.urlopen('http://web2py.com/appliances/default/show/%s' % i).read()
        title = re.compile('\<h2\>Appliance\s+\"(?P<title>.*?)\"').search(page).group('title')
        image = re.compile('/\S*\.png').search(page).group()
        url = re.compile('/\S*\.w2p').search(page).group()
        description = re.compile('\<h3\>Description.*?\[',re.DOTALL).search(page).group()[:-1]
    except Exception, e:
        print e
        continue
    else:	    
        print title
        print image
        print url
        folder = re.sub('\W','',title).lower()
        os.mkdir(folder)
        os.chdir(folder)
        open('web2py.app.%s.w2p' % folder,'wb').write(urllib.urlopen('http://web2py.com'+url).read())
        open('preview.png','wb').write(urllib.urlopen('http://web2py.com'+image).read())
        os.system('tar zxvf web2py.app.%s.w2p' % folder)
        open('ABOUT','w').write(description)
        os.chdir('..')
        d[i] = (title,image,url,description)
open('list.apps','w').write(repr(d))
