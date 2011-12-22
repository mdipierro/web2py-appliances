def error():
    raise HTTP(400)

def data():
    "http://trirand.com/blog/jqgrid/server.php?q=1&_search=false&nd=1267835445772&rows=10&page=1&sidx=amount&sord=asc&searchField=&searchString=&searchOper="
    from gluon.serializers import json
    import cgi
    tablename = request.vars.tablename or error()
    columns = (request.vars.columns or error()).split(',')
    rows=int(request.vars.rows or 25)
    page=int(request.vars.page or 0)
    sidx=request.vars.sidx or 'id'
    sord=request.vars.sord or 'asc'
    searchField=request.vars.searchField
    searchString=request.vars.searchString
    searchOper={'eq':lambda a,b: a==b,
                'nq':lambda a,b: a!=b,
                'gt':lambda a,b: a>b,
                'ge':lambda a,b: a>=b,
                'lt':lambda a,b: a<b,
                'le':lambda a,b: a<=b,
                'bw':lambda a,b: a.like(b+'%'),
                'bn':lambda a,b: ~a.like(b+'%'),
                'ew':lambda a,b: a.like('%'+b),
                'en':lambda a,b: ~a.like('%'+b),
                'cn':lambda a,b: a.like('%'+b+'%'),
                'nc':lambda a,b: ~a.like('%'+b+'%'),
                'in':lambda a,b: a.belongs(b.split()),
                'ni':lambda a,b: ~a.belongs(b.split())}\
                [request.vars.searchOper or 'eq']
    table=db[tablename]
    if request.vars.fieldname:
        dbset = db(table[request.vars.fieldname]==request.vars.fieldvalue)
    else:
        dbset = db(table.id>0)
    if searchField: dbset=dbset(searchOper(table[searchField],searchString))
    orderby = table[sidx]
    if sord=='desc': orderby=~orderby
    limitby=(rows*(page-1),rows*page)
    fields = [table[f] for f in columns]
    records = dbset.select(orderby=orderby,limitby=limitby,*fields)
    nrecords = dbset.count()
    items = {}
    items['page']=page
    items['total']=int((nrecords+(rows-1))/rows)
    items['records']=nrecords
    readable_fields=[f.name for f in fields if f.readable]
    def f(value,fieldname):
        r = table[fieldname].represent
        if r: value=r(value)
        try: return value.xml()
        except: return cgi.escape(str(value))

    items['rows']=[{'id':r.id,'cell':[f(r[x],x) for x in readable_fields]} \
                       for r in records]
    return json(items)
