# -*- coding: utf-8 -*-
#########################################################################
## Author: Leonel Câmara
## File is released under public domain and you can use without limitations
#########################################################################

db = DAL('sqlite://storage.sqlite', pool_size=1, check_reserved=['all'])

def FILESIZE(table, fieldname):
    """
    Make a compute function for filesize of a given table's field.

    table -- name of the table with the field
    fieldname -- name of the field whose file we will use to calculate
    """
    def calc_size(row):
        import os
        fname, fstream = db[table][fieldname].retrieve(row[fieldname])
        fstream.seek(0, os.SEEK_END)
        size = fstream.tell()
        fstream.close()
        return size

    return calc_size


def upload_fullpath(tablename, filename, makedirs=False):
    """
    Given a tablename and a filename return the full path
    TODO: For now it assumes uploadseparate=True in the field definition,
          could be more versatile.
    """
    import os
    fieldname, img_uid = filename.split('.')[1:3]
    path = os.path.join(request.folder, 'uploads', tablename + '.' + fieldname, img_uid[:2], filename)
    if makedirs:
        try:
            os.makedirs(os.path.dirname(path))
        except OSError:
            print "Skipping creation of %s because it exists already." % os.path.dirname(path)
    return path


def SMARTHUMB(tablename, image, box, fit=True, name="thumb"):
    '''Downsample the image.
    http://www.web2pyslices.com/slice/show/1522/generate-a-thumbnail-that-fits-in-a-box

    Modified to respect uploadseparate=True differences

     @param img: Image -  an Image-object
     @param box: tuple(x, y) - the bounding box of the result image
     @param fit: boolean - crop the image to fill the box
    '''
    if image:
        from PIL import Image
        import os
        from gluon.tools import current, web2py_uuid
        request = current.request
        img = Image.open(upload_fullpath(tablename, image))
        #preresize image with factor 2, 4, 8 and fast algorithm
        factor = 1
        while img.size[0] / factor > 2 * box[0] and img.size[1] * 2 / factor > 2 * box[1]:
            factor *= 2
        if factor > 1:
            img.thumbnail((img.size[0] / factor, img.size[1] / factor), Image.NEAREST)
 
        #calculate the cropping box and get the cropped part
        if fit:
            x1 = y1 = 0
            x2, y2 = img.size
            wRatio = 1.0 * x2 / box[0]
            hRatio = 1.0 * y2 / box[1]
            if hRatio > wRatio:
                y1 = int(y2 / 2 - box[1] * wRatio / 2)
                y2 = int(y2 / 2 + box[1] * wRatio / 2)
            else:
                x1 = int(x2 / 2 - box[0] * hRatio / 2)
                x2 = int(x2 / 2 + box[0] * hRatio / 2)
            img = img.crop((x1, y1, x2, y2))
 
        #Resize the image with best quality algorithm ANTI-ALIAS
        img.thumbnail(box, Image.ANTIALIAS)
 
        root, ext = os.path.splitext(image)
        thumbname = '%s.thumbnail.%s.%s%s' % (tablename, web2py_uuid().replace('-', '')[-16:], web2py_uuid().replace('-', '')[-16:], ext)
        img.save(upload_fullpath(tablename, thumbname, makedirs=True))        

        return thumbname


db.define_table('testfile',
    Field('name', requires=[IS_NOT_EMPTY(), IS_NOT_IN_DB(db, 'testfile.name', error_message='You already submitted a file by that name')], unique=True, notnull=True),
    Field('fsize', 'integer', compute=FILESIZE('testfile', 'image')),
    Field('image', 'upload', uploadseparate=True, autodelete=True, requires=[IS_NOT_EMPTY(), IS_LENGTH(maxsize=42204800, error_message=T('The Image must be smaller than 200KB')), IS_IMAGE()]),
    Field('thumbnail','upload', uploadseparate=True, readable=False, writable=False, autodelete=True, compute=lambda row: SMARTHUMB('testfile', row.image, (200, 150))),
)

