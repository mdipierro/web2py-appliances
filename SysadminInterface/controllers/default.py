# This sees request, response, session, expose, redirect, HTTP

############################################################
### import required modules/functions
############################################################
from gluon.fileutils import listdir, cleanpath, tar, tar_compiled, untar
from gluon.languages import findT, update_all_languages
from gluon.myregex import *
from gluon.restricted import *
from gluon.compileapp import compile_application, remove_compiled_application
import time,os,sys,re,cgi

############################################################
### make sure administrator is on localhost
############################################################

from gluon.contenttype import contenttype
from gluon.fileutils import check_credentials

if request.env.remote_addr!=request.env.http_host.split(':')[0]:
    raise HTTP(400)
if not check_credentials(request):
    redirect('/admin')
else:
    session.authorized=True

############################################################
### generate menu
############################################################

_a,_f=request.application, request.function
response.menu=[]
response.menu.append(('proc',_f=='proc','/%s/default/proc'%_a))
response.menu.append(('net',_f=='net','/%s/default/net'%_a))
response.menu.append(('etc',_f=='etc','/%s/default/etc'%_a))
response.menu.append(('var',_f=='var','/%s/default/var'%_a))
response.menu.append(('logout',False,'/%s/default/logout'%_a))
if not session.authorized: response.menu=[('login',True,'')]

############################################################
### exposed functions
############################################################

def index():
    redirect(URL('proc'))

def logout():
    session.authorized=None
    redirect(URL('index'))

def markup(text):
    text=cgi.escape(text)
    items=re.compile('\W(?P<name>[\w\-]+@[\w\-]+(\.[\w\-]+)+)[^\w\-]').findall(text)
    done={}
    for item in items:
        if done.has_key(item): continue
        done[item]=1
        text=text.replace(item[0],A(item[0],_href="mailto:%s" %item[0]).xml())
    items=re.compile('[^\w\-](?P<name>http\://[\w\-]+(\.[\w\-]+)+)[^\w\-]').findall(text)
    done={}
    for item in items:
        if done.has_key(item): continue
        done[item]=1
        text=text.replace(item[0],A(item[0],_href="%s" %item[0]).xml())
    items=re.compile('[^0-9](?P<name>[0-9]+(\.[0-9]+){3})[^0-9]').findall(text)
    done={}
    for item in items:
        if done.has_key(item): continue
        done[item]=1
        text=text.replace(item[0],A(item[0],_href="whois/%s" %item[0]).xml())
    return XML(text)

def proc():
    os.system('ps auxw > applications/sysadmin/cache/ps.tmp')
    table=TABLE()
    table.components.append(TR(TH('USER'),TH('PID'),TH(),TH('%CPU'),TH('%MEM'), 
                               TH('VSZ'),TH('RSS'),TH('TT'),TH('STAT'),
                               TH('STARTED'),TH('TIME'),TH('COMMAND')))
    for line in open('applications/sysadmin/cache/ps.tmp','r').readlines()[1:]:
        items=line.split()
        items[0]=A(items[0],_href=URL('finger/'+items[0]))
        items[10]=DIV(A(items[10]+' ',_href=URL('man/'+items[10])),
                      ' '+' '.join(items[11:]))
        items.insert(2,A('kill',_href=URL('kill/'+items[1])))
        table.components.append(TR(*items[:12]))
    return dict(table=table)   

def finger():
    os.system('finger %s > applications/sysadmin/cache/finger.tmp' % request.args[0])
    return dict(finger=open('applications/sysadmin/cache/finger.tmp','r').read())

def kill():
    os.system('kill -9 %s' % request.args[0])
    session.flash='process %s killed' % request.args[0]
    redirect(URL('proc'))

def man():
    command=request.args[-1]
    os.system('info %s > applications/sysadmin/cache/man.tmp' % command)
    man=open('applications/sysadmin/cache/man.tmp','r').read()
    return dict(command=command,man=man)

def net():
    os.system('netstat -na > applications/sysadmin/cache/netstat.tmp')
    table=TABLE()
    table.components.append(TR(TH('Local'),TH('Foreign'),TH('State')))
    for line in open('applications/sysadmin/cache/netstat.tmp','r').readlines()[1:]:
        items=line.split()
        if len(items)==6 and items[5] in ['LISTEN','ESTABILISHED','CLOSE_WAIT',
           'SYN_RCVD','SYN_SENT','LAST_ACK','FIN_WAIT_1',
           'FIN_WAIT_2','CLOSING','TIME_WAIT']:
            items[3]=items[3].split('.')
            ip,port='.'.join(items[3][:-1]),items[3][-1]
            items[3]=ip+':'+port
            items[4]=items[4].split('.')
            ip,port='.'.join(items[4][:-1]),items[4][-1]
            if ip!='*' and ip!='127.0.0.1':
                items[4]=DIV(A(ip,_href=URL('whois/'+ip)),':'+port)
            else: items[4]=ip+':'+port
            table.components.append(TR(items[3],items[4],items[5]))
    os.system('ifconfig > applications/sysadmin/cache/ifconfig.tmp')
    ifconfig=markup(open('applications/sysadmin/cache/ifconfig.tmp','r').read())
    os.system('arp -a > applications/sysadmin/cache/arp.tmp')
    arp=open('applications/sysadmin/cache/arp.tmp','r').read()
    return dict(table=table,ifconfig=ifconfig,arp=arp)

def whois():
    os.system('whois %s > applications/sysadmin/cache/whois.tmp' % request.args[0])
    return dict(whois=markup(open('applications/sysadmin/cache/whois.tmp','r').read()))

def etc():
    os.system('users > applications/sysadmin/cache/users.tmp')
    users=open('applications/sysadmin/cache/users.tmp','r').readlines()
    os.system('service --list  > applications/sysadmin/cache/service.tmp')
    services=open('applications/sysadmin/cache/service.tmp','r').readlines()
    services_on={}
    for service in services:
        if os.system('service --test-if-configured-on '+service):
            services_on[service]=False
        else: services_on[service]=True
    return dict(users=users, services=services_on)

def var():
    return dict()

def edit():
    return HTML(BODY(H1('not implemented'))).xml()