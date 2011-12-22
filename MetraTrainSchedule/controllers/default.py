response.menu=[
  ['search',request.function=='index',URL('index')],
  ['metra',False,'http://www.metrarail.com']]

def within_6h(a,b): return (a-b+1440)%1440<720 

def lcs(line1,line2):
    l1=len(line1)
    l2=len(line2)
    k=[[0 for i in xrange(l2)] for j in xrange(l1)]
    for i in xrange(l1):
        for j in xrange(l2):
           if line1[i]==line2[j]:
               if i>0 and j>0: k[i][j]=k[i-1][j-1]+1
               else: k[i][j]=1
           else:
               if i>0: k[i][j]=k[i-1][j]
               if j>0 and k[i][j-1]>k[i][j]: k[i][j]=k[i][j-1]
    return k[l1-1][l2-1]

def get_stations(name):
   name=name.lower()
   s=[]
   y=0.0
   for id,station in stations.items():
       ell=lcs(station.lower(),name)
       x=float(ell)/len(name)
       if ell<4: continue
       if x==y : s.append(id)
       if x>y: s,y=[id],x
   return tuple(s)

class LENGTH:
    def __call__(self,value):
        if len(value)==0: return (value,'Required')
        if len(value)<4 or len(value)>30: return (value,'Invalid Station Name')
        return (value,None)

def index():
    if request.vars.when: when=request.vars.when
    elif today.weekday()<5: when='Weekday'
    elif today.weekday()==5: when='Saturday'
    elif today.weekday()==6: when='Sunday'
    if not request.vars.departure and not request.vars.arrival and \
       session.vars:
         request.vars.departure=session.vars.departure
         request.vars.arrival=session.vars.arrival
    form=FORM(TABLE(TR('Departure Station:',INPUT(_name='departure',requires=LENGTH())),
                    TR('Arrival Station:',INPUT(_name='arrival',requires=LENGTH())),
                    TR('When:',SELECT('Weekday','Saturday','Sunday',_name='when',value=when)),
                    TR('',INPUT(_type='submit'))),_method="GET")
    a,b,trains=[],[],[]
    if (request.vars.arrival or request.vars.departure) and form.accepts(request,formname=None,keepvalues=True):
        session.vars=form.vars
        a=get_stations(form.vars.departure)
        b=get_stations(form.vars.arrival)
        if not len(a):
           form.errors['departure']='unkown station'
        elif not len(b):
           form.errors['arrival']='unkown station'
        else:
           if form.vars.when=='Weekday':
               when_query=(db.arrival.weekday==True)&(db.departure.weekday==True)
           elif form.vars.when=='Saturday':
               when_query=(db.arrival.saturday==True)&(db.departure.saturday==True)
           elif form.vars.when=='Sunday':
               when_query=(db.arrival.sunday==True)&(db.departure.sunday==True)
           trains=db(db.arrival.line==db.departure.line)\
                    (db.arrival.number==db.departure.number)\
                    (db.departure.station.belongs(a))\
                    (db.arrival.station.belongs(b))\
                    (when_query).select(orderby=db.departure.time,\
                                        cache=(cache.ram,3600))
           trains=[x for x in trains if within_6h(x.arrival.time,x.departure.time)]
           if not len(trains): response.flash='no trains between selected destinations'
    if not request.vars.when: request.vars.when=when
    return dict(form=form,a=a,b=b,trains=trains)

def train():
    if len(request.args)<2: redirect(URL('index'))
    when=request.args[0]
    if when=='Weekday':
        c1,c2=db.departure.weekday==True, db.arrival.weekday==True
    elif when=='Saturday':
        c1,c2=db.departure.saturday==True, db.arrival.saturday==True
    elif when=='Sunday':
        c1,c2=db.departure.sunday==True, db.arrival.sunday==True
    else:
        redirect(URL('index'))
    rows1=db(db.departure.number==request.args[1])\
            (db.station.id==db.departure.station)\
            (c1).select(groupby=db.departure.station,orderby=db.departure.time,cache=(cache.ram,3600))
    rows2=db(db.arrival.number==request.args[1])\
            (db.station.id==db.arrival.station)\
            (c2).select(groupby=db.arrival.station,orderby=db.arrival.time,cache=(cache.ram,3600))
    if not len(rows1)==len(rows2) or len(rows1)<1:
        session.flash='invalid train number'
        redirect(URL('index'))
    return dict(rows1=rows1,rows2=rows2)

def station():
    if len(request.args)<1: redirect(URL('index'))
    i=int(request.args[0])
    if not stations.has_key(i):
        redirect(URL('index'))
    redirect('http://maps.google.com/maps?q=%s+Station,+il' % stations[i])