EMAIL_VERIFICATION=False
MAIN=URL(r=request,c='news',f='index')
LOGIN=URL(r=request,c='default',f='login')
LOGOUT=URL(r=request,c='default',f='logout')
SECONDS=1.0
PAGE_LOCK_TIME=180*SECONDS
PAGE_LOCK_RENEW_TIME=120*SECONDS
ERROR=URL(r=request,c='default',f='index')
HOST='http://'+request.env.http_host
EMAIL_SERVER="localhost:25"
EMAIL_SENDER="nobody@somewhere.com"

if HOST[:5]=='https': response.cookies[response.session_id_name]['secure']=True
