#from gluon.debug import dbg

def photo_gallery():
    """
    Allows to access the "photo_gallery" component
    """
    import random
    manager_toolbar = ManagerToolbar('image')
    MAX_IMAGES = WEBSITE_PARAMETERS.max_gallery_images_to_show if WEBSITE_PARAMETERS.max_gallery_images_to_show is not None else 5
    page = db.page(request.vars.container_id)
    if page:
        q=(db.image.show_in_gallery==1) & (db.image.page==page)
    else:
        q=(db.image.show_in_gallery==1)
    if db(q).isempty(): #if there are no images related to the page, we select all available images
        q=(db.image.show_in_gallery==1)
    images = sorted(db(q).select(cache=(cache.ram, 60), cacheable=True), key=lambda *args: random.random())[:MAX_IMAGES]
    
    return dict(images=images,
                manager_toolbar=manager_toolbar)


@auth.requires_membership('manager')
def delete_image():
    image = db.image(request.args(0))
    if image:  
        form = FORM.confirm(T('Yes, I really want to delete this image'),{T('Back'):URL('images')})
        if form.accepted:
            #remove image and thumb
            pathname = path.join(request.folder,'static','images', 'photo_gallery', str(form.vars.file))
            if path.exists(pathname):
                shutil.rmtree(pathname)
            pathname = path.join(request.folder,'static','images', 'photo_gallery', str(form.vars.thumb))
            if path.exists(pathname):
                shutil.rmtree(pathname)
            #remove the image
            db(db.image.id==image.id).delete()
            session.flash = T('Image deleted')
            redirect(URL('images'))
    return dict(image=image, form=form)

@auth.requires_membership('manager')
def edit_image():
    """
        Allows to add images in the library
    """
    thumb=""
    page = db.page(request.vars.container_id)
    if page:
        db.image.page.default = page.id
    if len(request.args):
        image = db(db.image.id==request.args(0)).select().first()
    if len(request.args) and image:
        form = SQLFORM(db.image, image, deletable=True, showid=False)
        thumb = image.thumb
    else:
        form = SQLFORM(db.image)
    if form.accepts(request.vars, session): 
        response.flash = T('form accepted')
        #resize the original image to a better size and create a thumbnail
        __makeThumbnail(db.image,form.vars.id,(800,800),(260,260))
        redirect(URL('images'))
    elif form.errors:
        response.flash = T('form has errors')
    return dict(form=form,list=list,thumb=thumb)

def images():
    manager_toolbar = ManagerToolbar('image')
    images = db(db.image).select(cache=(cache.ram, 60), cacheable=True, orderby=db.image.page)
    pages = list(set([i.page for i in images if i.page <> 0]))
    return dict(images=images,
                pages=pages,
                manager_toolbar=manager_toolbar)

def __makeThumbnail(dbtable,ImageID,image_size=(600,600), thumbnail_size=(260,260)):
    #dbg.set_trace() # stop here!
    try:    
        thisImage=db(dbtable.id==ImageID).select()[0]
        from PIL import Image
    except: return

    full_path = path.join(request.folder,'static','images','photo_gallery',thisImage.file)
    im = Image.open(full_path)
    im.thumbnail(image_size,Image.ANTIALIAS)
    im.save(full_path)
    thumbName='thumb.%s' % (thisImage.file)
    full_path = path.join(request.folder,'static','images','photo_gallery', 'thumbs',thumbName)
    try: 
        im.thumbnail(thumbnail_size,Image.ANTIALIAS)
    except:
        pass
    im.save(full_path)
    thisImage.update_record(thumb=thumbName)
    return

def nicedit_image_upload():
    """
    Controller to upload images with nicedit
    """
    from gluon.contrib.simplejson import dumps
    from os import mkdir
	
    page_id = request.args(0)
    pathname = path.join(request.folder,'static','images', 'pages_content', page_id)
    if not path.exists(pathname):
        mkdir(pathname)

    pathfilename = path.join(pathname, request.vars.image.filename)
    dest_file = open(pathfilename, 'wb')
    
    try:
        dest_file.write(request.vars.image.file.read())
    finally:
        dest_file.close()

    #Make a thumbnail (max 600*600px) of the uploaded Image
    try:
        from PIL import Image
        im = Image.open(pathfilename)
        im.thumbnail((600,600),Image.ANTIALIAS)
        im.save(pathfilename)
    except:
        pass
    links_dict = {"original":URL('static', 'images/pages_content/'+page_id+'/'+request.vars.image.filename)}
    set_dict = {"links" : links_dict}
    upload_dict = {"upload" : set_dict}

    return dumps(upload_dict)