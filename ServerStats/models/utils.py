def url(f,args=[]): return URL(r=request,f=f,args=args)
def button(text,action,args=[]):
    return SPAN('[',A(text,_href=URL(r=request,f=action,args=args)),']')

def link_server(server):
    return A(server.name,_href=url('view_server',server.id))

def link_platform(platform):
    return A(platform.name,_href=url('view_platform',platform.id))





