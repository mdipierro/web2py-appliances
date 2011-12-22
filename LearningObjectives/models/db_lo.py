db.define_table('school',
                Field('name',unique=True),
                format='%(name)s')
db.define_table('program',
                Field('school',db.school,default=1,writable=False),
                Field('name',unique=True),
                format='%(name)s')
db.define_table('learning_goal',
                Field('program',db.program,writable=False),                
                Field('body','text',required=True, comment=A('wiki syntax',_href='http://web2py.com/examples/static/markmin.html')),
                Field('f_what','list:string',label='What'),
                Field('f_how','list:string',label='How'),
                Field('f_when','list:string',label='When'),
                Field('f_who','list:string',label='Who'),
                Field('examples','list:string'))

if not db(db.school).count():
    db.school.insert(name="CDM")
if not db(db.program).count():
    programs=['Animation BS', 'Animation BA', 'Computer Game Development BS', 'Computer Graphics and Motion Technology BS',
              'Computer Science BS', 'Computing BA', 'Digital Cinema BS', 'Digital Cinema BA', 'Information Assurance and Security Engineering BS',
              'Information Systems BS', 'Information Technology BS', 'Information Technology BA',
              'Interactive Media BS', 'Math and Computer Science BS', 'Network Technology BS',
              'MS Applied Technology', 'MS Business Information Technology', 'MS Cinema Production',
              'MS Computer Game Development', 'MS Computer Graphics and Motion Technology',
              'MS Computational Finance', 'MS Computer Science', 'MS Computer, Information and Network Security',
              'MS E-Commerce Technology', 'MS Human-Computer Interaction', 'MS Information Systems',
              'MS Information Technology', 'MS IT Project Management', 'MS Network Engineering and Management',
              'MS Predictive Analytics', 'MS Software Engineering', 'JD/MA in Computer Science Technology',
              'JD/MS in Computer Science Technology']
    for program in programs:
        db.program.insert(name=program)
