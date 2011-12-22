def index():
    return HTML(TABLE(*[TR(IMG(_src=URL('example_%s.png'%x))) for x in ('hist','plot','color2d','scatter')]))
def example_hist(): return hist()
def example_plot(): return plot()
def example_color2d(): return color2d()
def example_scatter(): return scatter()

def pi():
    p = [(random.random(),random.random()) for i in range(1000)]
    n,k,z=0,0,[]    
    for x,y in p:
        if x**2+y**2<1: k+=1
        n+=1
        z.append((n,4.0*float(k)/n))
    session.mpl_p=p
    session.mpl_z=z
    return dict(table=TABLE(TR(IMG(_src=URL('plot1.png'))),
                            TR(IMG(_src=URL('plot2.png'))),
                            TR(IMG(_src=URL('plot3.png'))),
                            TR(IMG(_src=URL('plot4.png'))),
                            TR(IMG(_src=URL('plot5.png')))))

def plot1(): 
    q = [(x,y,0.01,0.01,0,1,0) for x,y in session.mpl_p if x**2+y**2<1]
    q += [(x,y,0.01,0.01,1,0,0) for x,y in session.mpl_p if x**2+y**2>1]
    return scatter(data=q,title='random points')

def plot2(): 
    return plot(data={'pi':session.mpl_z,'error':[(x,abs(y-3.14159)) for x,y in session.mpl_z]},title='4.0*N(in)/N(total)',xlab='N(total)',ylab='pi')

def plot3(): 
    return hist(data=[x for x,y in session.mpl_p],title='x distribution',
                ylab='')

def plot4(): 
    return hist(data=[y for x,y in session.mpl_p],title='y distribution',
                xlab='y',ylab='')

def plot5(): 
    data=[[0] * 20 for i in range(20)]
    for x,y in session.mpl_p:        
        data[int(x*20)][int(y*20)]+=1
    return color2d(data=data, title='density of points')
