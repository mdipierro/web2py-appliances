import os, stat, time, logging

def FullPath(file):
	return request.folder+'/uploads/'+file

while True:

	files=[(os.stat(FullPath(file))[stat.ST_CTIME],file) for file in os.listdir (request.folder+'/uploads') if file[:21]=='videos.uploaded_video']
	files.sort()


	for file in files:

		f_original = file[1]
		#original filename, replace uploaded_video with converted_video, exchange extension with new file extension
		f_converted = file[1].replace('.uploaded_video.','.converted_video.').rpartition('.')[0]+'.flv'
		f_image = file[1].replace('.uploaded_video.','.converted_image.').rpartition('.')[0]+'.png'

		try:
			os.system('ffmpeg -i %s -ar 44100 -s 400x300 -aspect 4:3 -f flv -y %s' % (FullPath(f_original),FullPath(f_converted)))
			os.system('ffmpeg -i %s -an -s 400x300 -aspect 4:3 -ss 00:00:03 -r 1 -vframes 1 -vcodec png -f rawvideo -y %s' % (FullPath(f_original),FullPath(f_image)))
			os.system('flvtool2 -U %s' % (FullPath(f_converted)))

			db(db.videos.uploaded_video==f_original).update(uploaded_video='' , converted_video=f_converted , converted_image = f_image, converted=True)
			db.commit()

		except:
			print "EXCEPTION"
			db(db.videos.uploaded_video==f_original).update(uploaded_video='' , conversion_error=True)
			db.commit()
			#logging.error('unable to convert %s'%(f_original))

		else:
			#always dispose of the original, user should be reprompted to upload video by ajax routine
			os.unlink(FullPath(f_original))


	time.sleep(5)