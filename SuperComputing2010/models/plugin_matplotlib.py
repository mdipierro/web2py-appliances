import os, tempfile, random, cStringIO
os.environ['MPLCONfigureDIR'] = tempfile.mkdtemp()
try:
    from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
    from matplotlib.figure import Figure
    from matplotlib.patches import Ellipse
except ImportError:
    raise HTTP(200, "requires mathplotlib installed")

def hist(title='title',xlab='x',ylab='y',
         data=[1,2,3,3,4,5,5,6,7,7,8,2,3,4,3,4,6]):
    figure=Figure(frameon=False)
    figure.set_facecolor('white')
    axes=figure.add_subplot(111)
    if title: axes.set_title(title)
    if xlab: axes.set_xlabel(xlab)
    if ylab: axes.set_ylabel(ylab)
    ell=axes.hist(data,20)
    canvas=FigureCanvas(figure)    
    stream=cStringIO.StringIO()
    canvas.print_png(stream)   
    return stream.getvalue()
    

def plot(title='title',xlab='x',ylab='y',
         data={'xxx':[(0,0),(1,1),(1,2),(3,3)],
               'yyy':[(0,0,.2),(2,1,0.2),(2,2,0.2),(3,3,0.2)]}):
    figure=Figure(frameon=False)
    axes=figure.add_subplot(111)
    if title: axes.set_title(title)
    if xlab: axes.set_xlabel(xlab)
    if ylab: axes.set_ylabel(ylab)
    keys=sorted(data)
    for key in keys:
        stream = data[key]
        (x,y)=([],[])
        yerr = []
        for point in stream:
            x.append(point[0])
            y.append(point[1])
            if len(point)==3:
                yerr.append(point[2])
        ell=axes.plot(x, y, linewidth="2")
        if len(yerr)==len(x):
            axes.errorbar(x, y, yerr=yerr, fmt='o', linewidth="1")        
    canvas=FigureCanvas(figure)    
    stream=cStringIO.StringIO()
    canvas.print_png(stream)    
    return stream.getvalue()


def color2d(title='title',xlab='x',ylab='y',
            data=[[1,2,3,4],[2,3,4,5],[3,4,5,6],[4,5,6,7]]):
    figure=Figure()
    figure.set_facecolor('white')
    axes=figure.add_subplot(111)
    if title: axes.set_title(title)
    if xlab: axes.set_xlabel(xlab)
    if ylab: axes.set_ylabel(ylab)
    image=axes.imshow(data)
    image.set_interpolation('bilinear')
    canvas=FigureCanvas(figure)
    stream=cStringIO.StringIO()
    canvas.print_png(stream)
    return stream.getvalue()


def scatter(title='title',xlab='x',ylab='y',
            data=None):
    if data==None:
        r=random.random
        data=[(r()*10,r()*10,r(),r(),r(),r(),r()) for i in range(100)]
    figure=Figure()
    figure.set_facecolor('white')
    axes=figure.add_subplot(111)
    if title: axes.set_title(title)
    if xlab: axes.set_xlabel(xlab)
    if ylab: axes.set_ylabel(ylab)
    for i,p in enumerate(data):
        p=list(p)
        while len(p)<4: p.append(0.01)
        e=Ellipse(xy=p[:2],width=p[2],height=p[3])
        axes.add_artist(e)
        e.set_clip_box(axes.bbox)
        e.set_alpha(0.5)
        if len(p)==7:
            e.set_facecolor(p[4:])    
        data[i]=p
    axes.set_xlim(min(p[0]-p[2] for p in data), max(p[0]+p[2] for p in data))
    axes.set_ylim(min(p[1]-p[3] for p in data), max(p[1]+p[3] for p in data))
    canvas=FigureCanvas(figure)
    stream=cStringIO.StringIO()
    canvas.print_png(stream)
    return stream.getvalue()
