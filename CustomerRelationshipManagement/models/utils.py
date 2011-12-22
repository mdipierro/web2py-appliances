def url(f,args=[]): return URL(r=request,f=f,args=args)
def button(text,action,args=[]):
    return SPAN('[',A(text,_href=URL(r=request,f=action,args=args)),']')

def link_person(person):
    return A(person.name,_href=url('view_person',person.id))

def link_company(company):
    return A(company.name,_href=url('view_company',company.id))
