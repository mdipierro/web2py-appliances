# -*- coding: utf-8 -*- 
### required - do no delete
def user(): return dict(form=auth())
def download(): return response.download(request,db)
def call():
    session.forget()
    return service()
### end requires
def index():
    return dict()

def error():
    return dict()

@auth.requires_login()
def experiment_create():
    form=crud.create(db.t_experiment,next='experiment_read/[id]')
    return dict(form=form)

def propagate_wave(slits):
    import math, cmath
    wave1=[]
    for p in slits:
        r=math.sqrt(100.+p**2)
        wave1.append(cmath.exp(2j*math.pi*r)/r)
    I=[]
    for q in range(-25,25):
        w=0.0
        for i,p in enumerate(slits):
            r=math.sqrt(100.+(q-p)**2)
            w+=wave1[i]*cmath.exp(2j*math.pi*r)/r
        I.append((q,w))
    return I
    
def propagate_photons(slits):
    import math, cmath
    wave1=[]
    for p in slits:
        r=math.sqrt(100.+p**2)
        wave1.append(cmath.exp(2j*math.pi*r)/r)
    Q=[]
    for i in range(1000):
        q = random.random()*50-25
        w=0.0
        for i,p in enumerate(slits):
            r=math.sqrt(100.+(q-p)**2)
            w+=wave1[i]*cmath.exp(2j*math.pi*r)/r
        if random.random()*0.0001<abs(w)**2:
            Q.append((q,50*random.random(),1,1))        
    return Q
    
@auth.requires_login()
def experiment_read():
    record = db.t_experiment(request.args(0)) or redirect(URL('error'))
    form=crud.read(db.t_experiment,record) 
    slits = [float(s) for s in record.f_slits]
    session.wave=propagate_wave(slits)
    session.photons=propagate_photons(slits)
    return dict(form=form,
                table=TABLE(TR(IMG(_src=URL('plot_wave.png'))),
                            TR(IMG(_src=URL('plot_interference.png'))),
                            TR(IMG(_src=URL('plot_photons.png'))),
                            TR(IMG(_src=URL('hist_photons.png'))),
                            TR(IMG(_src=URL('density_photons.png')))))
    
def plot_wave():
    return plot(data={'real':[(x,y.real) for x,y in session.wave],
                      'imag':[(x,y.imag) for x,y in session.wave]})

def plot_interference():
    return plot(data={'interferemce':[(x,abs(y)**2) for x,y in session.wave]})

def plot_photons():
    return scatter(data=session.photons)    
    
def hist_photons():
    return hist(data=[x for x,y,dx,dy in session.photons])        

def density_photons():
    return color2d(data=[[abs(y)**2 for x,y in session.wave]]*30)

@auth.requires_login()
def experiment_update():
    record = db.t_experiment(request.args(0),active=True) or redirect(URL('error'))
    form=crud.update(db.t_experiment,record,next='experiment_read/[id]',
                     ondelete=lambda form: redirect(URL('experiment_select')),
                     onaccept=crud.archive)
    return dict(form=form)

@auth.requires_login()
def experiment_select():
    f,v=request.args(0),request.args(1)
    query=f and db.t_experiment[f]==v or db.t_experiment
    rows=db(query)(db.t_experiment.active==True).select()
    return dict(rows=rows)

@auth.requires_login()
def experiment_search():
    form, rows=crud.search(db.t_experiment,query=db.t_experiment.active==True)
    return dict(form=form, rows=rows)
