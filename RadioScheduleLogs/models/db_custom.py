db.define_table('program',
                Field('name',requires=IS_NOT_EMPTY()),
                Field('created_on','datetime',default=request.now,writable=False),
                Field('created_by',db.auth_user,default=auth.user_id,writable=False),
                format='%(name)s')

db.program.id.represent=lambda id: SPAN(A('show',_href=URL(r=request,c='default',f='show_program',args=id)),' ',A('edit',_href=URL(r=request,c='default',f='edit_program',args=id)))


db.define_table('music',
                Field('program',db.program),
                Field('date_onair','date'),
                Field('name',requires=IS_NOT_EMPTY()),
                Field('file','upload',requires=IS_NOT_EMPTY()),
                Field('created_on','datetime',default=request.now,writable=False),
                Field('created_by',db.auth_user,default=auth.user_id,writable=False),
                format='%(name)s')

obj="""<object type="application/x-shockwave-flash" data="%(player)s?&song_url=%(url)s&" width="17" height="17"><param name="movie" value="%(player)s?&song_url=%(url)s&" /> <img src="noflash.gif" width="17" height="17" alt="" /></object>"""

db.music.id.represent=lambda id: A('edit',_href=URL(r=request,c='default',f='edit_music',args=id))
db.music.file.represent=lambda file: SPAN(A('download',_href=URL(r=request,c='default',f='download',args=file)),XML(obj % dict(player=URL(r=request,c='static',f='musicplayer.swf'),url=URL(r=request,c='default',f='download',args=file))))
