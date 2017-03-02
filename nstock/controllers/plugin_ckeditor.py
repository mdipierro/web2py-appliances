# -*- coding: utf-8 -*-

import os
from gluon import *

def upload():
    (new_filename, old_filename, length,
     mime_type) = current.plugin_ckeditor.handle_upload()
    
    title = os.path.splitext(old_filename)[0]
    
    result = current.plugin_ckeditor.settings.table_upload.validate_and_insert(
        title=title,
        filename=old_filename,
        upload=new_filename,
        flength=length,
        mime_type=mime_type
    )
    
    text = ''
    url = URL(*current.plugin_ckeditor.settings.download_url,
              args=[new_filename])
    
    if not result.id:
        text = result.errors

    return dict(text=text, cknum=request.vars.CKEditorFuncNum, url=url)
        
def browse():
    db = current.plugin_ckeditor.db
    table_upload = current.plugin_ckeditor.settings.table_upload
    browse_filter = current.plugin_ckeditor.settings.browse_filter
    set = db(table_upload.id>0)
    for key, val in browse_filter.items():
        if value[0] == '<':
            set = set(table_upload[key]<value[1:])
        elif value[0] == '>':
            set = set(table_upload[key]>value[1:])
        elif value[0] == '!':
            set = set(table_upload[key]!=value[1:])
        else:
            set = set(table_upload[key]==value)
    
    rows = set.select(orderby=table_upload.title)
    
    return dict(rows=rows, cknum=request.vars.CKEditorFuncNum)
    
def delete():
    filename = request.args(0)
    if not filename:
        raise HTTP(401, 'Required argument filename missing.')
        
    db = current.plugin_ckeditor.db
    table_upload = current.plugin_ckeditor.settings.table_upload
    db(table_upload.upload == filename).delete()
    
    # delete the file from storage
    current.plugin_ckeditor.unlink(filename)

