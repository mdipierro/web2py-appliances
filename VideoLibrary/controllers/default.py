def index():
	records=db().select(db.videos.ALL)
	return dict(videos=records)

def show():
	id=request.vars.id
	videos=db(db.videos.id==id).select()
	if not len(videos):
		session.flash='Could not find cooresponding video'
		redirect(URL('index'))
	return dict(video=videos[0])

def delete():
	id=request.vars.id
	db(db.videos.id==id).delete()
	session.flash='V@deo Deleted'
	redirect(URL('index'))
	return dict()


def new_video():
	form=SQLFORM(db.videos, fields=['title','description','uploaded_video'])
	if form.accepts(request,session): #custom validator should confirm that video file is actually a video
		session.flash='Video successfully uploaded'
		redirect(URL('show?id='+str(form.vars.id)))
	return dict(form=form)