Link = db.define_table(
    'link',
    Field('url',unique=True),
    Field('visits','integer',default=0),
    Field('screenshot','upload',writable=False),
    format = '%(url)s')

Bookmark = db.define_table(
    'bookmark',
    Field('link','reference link',writable=False),
    Field('category',requires=IS_IN_SET(['work','personal'])),
    Field('tags','list:string'),
    auth.signature)

def toCode(id):
    s,c = 'GKys67LJPDAFvcEp9rkwRd43fCjbxSXzMTQ28hgeUWuNYmqZt5VanBH',''
    while id: c,id = c+s[id % 55], id//55
    return c

def toInt(code):
    s,id = 'GKys67LJPDAFvcEp9rkwRd43fCjbxSXzMTQ28hgeUWuNYmqZt5VanBH',0
    for i in range(len(code)): id += s.find(code[i])*55**i
    return id

def shorten(id, row):
    s = URL('visit',args=toCode(id),scheme=True)
    return A(s,_href=s)

Bookmark.link.represent = shorten
Bookmark.id.readable = False
Bookmark.is_active.readable = False
Bookmark.is_active.writable = False
