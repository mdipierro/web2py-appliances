db.define_table('magazine',
                Field('volume','integer'),
                Field('issue','integer'),
                Field('title'),
                Field('pub_date','date'),
                Field('image',default='cover.1.1.gif'))

db.define_table('article',
                Field('magazine',db.magazine),
                Field('sortable','integer'),
                Field('title'),
                Field('link'))

db.define_table('author',
                Field('article',db.article),
                Field('name'),
                Field('link'))

if not db(db.magazine).count():
    for i in range(1,5):
        for j in range(1,2):
            id = db.magazine.insert(volume=i,issue=j,title='Scientific Python')
            k = db.article.insert(title='From the Editors: Watchful Waiting',link='http://link.aip.org/link/CSENFA/v13/i2/p3?prog=normal',magazine=id,sortable=0)
            db.author.insert(article=k,name='I. Beichl')
            k = db.article.insert(title='Books',link='http://link.aip.org/link/CSENFA/v13/i2/p5?prog=normal',magazine=id,sortable=1)
            db.author.insert(article=k,name='E. Ayars')

            k = db.article.insert(title='Python for Scientists and Engineers',link='http://link.aip.org/link/CSENFA/v13/i2/p9?prog=normal',magazine=id,sortable=2)
            db.author.insert(article=k,name='K. Jarrod Millman')
            db.author.insert(article=k,name='M. Aivazis')
            k = db.article.insert(title='Python: An Ecosystem for Scientific Computing',link='http://link.aip.org/link/CSENFA/v13/i2/p13?prog=normal',magazine=id,sortable=3)
            db.author.insert(article=k,name='S. van der Walt')
            db.author.insert(article=k,name='S. Chris Colbert')
            db.author.insert(article=k,name='G. Varoquaux')
            k = db.article.insert(title='Cython: The Best of Both Worlds',link='http://link.aip.org/link/CSENFA/v13/i2/p31?prog=normal',magazine=id,sortable=4)
            for n in 'S. Behnel, R. Bradshaw, C. Citro, L. Dalcin, D. Sverre Seljebotn, K. Smith'.split(', '):
                db.author.insert(article=k,name=n)
            k = db.article.insert(title='Mayavi: 3D Visualization of Scientific Data',link='http://link.aip.org/link/CSENFA/v13/i2/p40?prog=normal',magazine=id,sortable=5)
            db.author.insert(article=k,name='P. Ramachandran')
            db.author.insert(article=k,name='G. Varoquaux')

            k = db.article.insert(title='A High-End Reconfigurable Computation Platform for Nuclear and Particle Physics Experiments',link='http://link.aip.org/link/CSENFA/v13/i2/p52?prog=normal',magazine=id,sortable=6)
            db.author.insert(article=k,name='M. Liu')

            k = db.article.insert(title='web2py for Scientific Applications',link='http://link.aip.org/link/CSENFA/v13/i2/p64?prog=normal',magazine=id,sortable=7)
            db.author.insert(article=k,name='M. Di Pierro')

            k = db.article.insert(title='A Report From VisWeek 2010',link='http://link.aip.org/link/CSENFA/v13/i2/p70?prog=normal',magazine=id,sortable=8)
            for n in 'C. Scheidegger, C. T. Silva, D. Weiskopf'.split(', '): db.author.insert(article=k,name=n)

            k = db.article.insert(title='From Equations to Code: Automated Scientific Computing',link='http://link.aip.org/link/CSENFA/v13/i2/p78?prog=normal',magazine=id,sortable=9)
            db.author.insert(article=k,name='A. R. Terrel')

            k = db.article.insert(title='EcoG: A Power-Efficient GPU Cluster Architecture for Scientific Computing',link='http://link.aip.org/link/CSENFA/v13/i2/p83?prog=normal',magazine=id,sortable=10)
            for n in 'M. Showerman, J. Enos, C. Steffen, S. Treichler, W. Gropp, W. W. Hwu'.split(', '): db.author.insert(article=k,name=n)

            k = db.article.insert(title='Last Word: Buying a House, Then and Now',link='http://cise.aip.org/vsearch/servlet/VerityServlet?KEY=ALL&uSeDeFaUlTkEy=TrUe&possible1=Day%2C+Charles&possible1zone=author&maxdisp=25&smode=strresults&aqs=true',magazine=id,sortable=11)
            db.author.insert(article=k,name='C. Day')

EXTRA = {}
LATEX = '<img src="http://chart.apis.google.com/chart?cht=tx&chl=%s" align="center"/>'
EXTRA['latex'] = lambda code: LATEX % code.replace('"','\"')
