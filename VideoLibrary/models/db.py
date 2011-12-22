import datetime; now=datetime.date.today()

db=DAL("sqlite://db.db")

db.define_table('videos',
	Field('title'),
	Field('description',length=256),
	Field('date','date',default=now),
	Field('uploaded_video','upload'),
	Field('converted_video','upload',default=''),
	Field('converted_image','upload',default=''),
	Field('converted','boolean',default=False),
	Field('conversion_error','boolean',default=False))

db.videos.title.requires=[IS_NOT_EMPTY()]
db.videos.description.requries=[IS_NOT_EMPTY()]
db.videos.date.requires=[IS_DATE()]