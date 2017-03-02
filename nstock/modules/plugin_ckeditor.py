#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
web2py_ckeditor4: web2py plugin for CKEditor v4: http://ckeditor.com/
"""

__author__ = 'Tim Richardson'
__email__ = 'tim@growthpath.com.au'
__copyright__ = 'Copyright(c) 2012-2014, Ross Peoples, Bruno Rocha, ' \
                'Tim Richardson'
__license__ = 'LGPLv3'
__version__ = '1.1'
# possible options: Prototype, Development, Production
__status__ = 'Development'

import os
from gluon import *
from gluon.storage import Storage
from gluon.sqlhtml import FormWidget

class CKEditor(object):
    """
    Integrates CKEditor nicely into web2py.
    """
    def __init__(self, db, download_url=('default','download')):
        """
        Initializes the CKEditor module. Requires a DAL instance.
        """

        self.db = db

        self.settings = Storage()
        self.settings.table_upload = None
        self.settings.uploadfs = None
        self.settings.table_upload_name = 'plugin_ckeditor_upload'
        self.settings.extra_fields = {}
        self.settings.url_upload = URL('plugin_ckeditor', 'upload')
        self.settings.url_browse = URL('plugin_ckeditor', 'browse')
        self.settings.browse_filter = {}
        self.settings.file_length_max = 10485760    # 10 MB
        self.settings.file_length_min = 0           # no minimum
        self.settings.spellcheck_while_typing = False

        self.settings.download_url = download_url
        current.plugin_ckeditor = self

    def define_tables(self, migrate=True, fake_migrate=False):
        """
        Called after settings are set to create the required tables for dealing
        with file uploads from CKEditor.
        """
        upload_name = self.settings.table_upload_name

        self.settings.table_upload = self.db.define_table(upload_name,
            Field('title', length=255),
            Field('filename', length=255),
            Field('flength', 'integer'),
            Field('mime_type', length=128),
            Field('upload', 'upload', uploadfs=self.settings.uploadfs, requires=[IS_NOT_EMPTY(), IS_LENGTH(maxsize=self.settings.file_length_max, minsize=self.settings.file_length_min)]),
            *self.settings.extra_fields.get(upload_name, []),
            migrate = migrate,
            fake_migrate = fake_migrate,
            format = '%(title)s'
        )


    def widget(self, field, value, **attributes):
        """
        To be used with db.table.field.widget to set CKEditor as the desired
        widget for the field. Simply set
        db.table.field.widget = ckeditor.widget to use the CKEditor widget.
        """
        default = dict(
            value = value,
            _cols = 80,
            _rows = 10
        )

        attributes = FormWidget._attributes(field, default, **attributes)
        attributes['_class'] = 'text plugin_ckeditor'

        textarea = TEXTAREA(**attributes)
        javascript = self.load('#' + textarea.attributes['_id'],
                               use_caching=False)
        result = CAT(textarea, javascript)

        return result

    def handle_upload(self):
        """
        Gets an upload from CKEditor and returns the new filename that
        can then be inserted into a database. Returns (new_filename,
        old_filename, length, mime_type)
        """
        upload = current.request.vars.upload
        path = os.path.join(current.request.folder, 'uploads')

        if upload != None:
            if hasattr(upload, 'file'):
                form = SQLFORM.factory(
                    Field('upload', 'upload', requires=IS_NOT_EMPTY(),
                          uploadfs=self.settings.uploadfs,
                          uploadfolder=path),
                    table_name=self.settings.table_upload_name,

                )

                old_filename = upload.filename
                new_filename = form.table.upload.store(upload.file,
                                                       upload.filename)
                if self.settings.uploadfs:
                    length = self.settings.uploadfs.getsize(new_filename)
                else:
                    length = os.path.getsize(os.path.join(path, new_filename))
                mime_type = upload.headers['content-type']

                return (new_filename, old_filename, length, mime_type)
            else:
                raise HTTP(401, 'Upload is not proper type.')
        else:
            raise HTTP(401, 'Missing required upload.')

    def unlink(self, filename):
        """
        Unlink file from storage. It can be an local storage or a filesystem.
        Using self.unlink and clean file with filename.
        """
        if self.settings.uploadfs:
            self.settings.uploadfs.remove(filename)
        else:
            filepath = os.path.join(current.request.folder, 'uploads', filename)
            os.unlink(filepath)

    def load(self, selector=None, use_caching=True):
        """
        Generates the required JavaScript for CKEditor. If selector is set,
        then immediately turns the selected HTML element(s) into CKEditor
        instances. Otherwise, a manual JavaScript call to plugin_ckeditor_init()
        is required with the desired selector.
        """
        if self.settings.loaded and use_caching:
            return XML('')
        else:
            self.settings.loaded = True

        upload_url = self.settings.url_upload
        browse_url = self.settings.url_browse
        ckeditor_js = URL('static', 'plugin_ckeditor/ckeditor.js')
        jquery_js = URL('static', 'plugin_ckeditor/adapters/jquery.js')

        # contents_css = "['%s']" % URL('static', 'plugin_ckeditor/contents.css')
        contents_css = "['%s']" % URL('static', 'plugin_ckeditor/style.css')

        immediate = ''
        if selector:
            immediate = """
                jQuery(function() {
                    CKEDITOR.timestamp='ABCD';
                    var config = ckeditor_config();
                    jQuery('%s').ckeditor(config);
                });
            """ % selector

        scayt = 'false'
        if self.settings.spellcheck_while_typing:
            scayt = 'true'

        return XML(
            """

            <script type="text/javascript" src="%(ckeditor_js)s"></script>
            <script type="text/javascript" src="%(jquery_js)s"></script>

            <script type="text/javascript">
                function ckeditor_config() {
                    return {
                        contentsCss: %(contents_css)s,
                        // filebrowserUploadUrl: '%(upload_url)s',
                        // filebrowserBrowseUrl: '%(browse_url)s',
                        /*
                        toolbar: [
                            {name: 'clipboard', items: ['Cut', 'Copy', 'Paste', 'PasteText', 'PasteFromWord', '-', 'Undo', 'Redo']},
                            {name: 'editing', items: ['Find', 'Replace', '-', 'SelectAll', '-', 'SpellChecker', 'Scayt']},
                            {name: 'links', items: ['Link', 'Unlink', 'Anchor']},
                            {name: 'insert', items: ['Image', 'Flash', 'Table', 'SpecialChar']},
                            {name: 'tools', items: ['Maximize', 'ShowBlocks', '-', 'Source']},
                            '/',
                            {name: 'styles', items: ['Format', 'Font', 'FontSize']},
                            {name: 'basicstyles', items: ['Bold', 'Italic', 'Underline', 'Strike', '-', 'RemoveFormat']},
                            {name: 'paragraph', items: ['NumberedList', 'BulletedList', '-', 'Outdent', 'Indent', 'JustifyLeft', 'JustifyCenter', 'JustifyRight', 'JustifyBlock']},
                        ],*/
                        scayt_autoStartup: %(scayt)s,
                    }
                }
                %(immediate)s
            </script>
            """ % dict(
                ckeditor_js = ckeditor_js,
                jquery_js = jquery_js,

                contents_css = contents_css,
                upload_url = upload_url,
                browse_url = browse_url,
                scayt = scayt,
                immediate = immediate,
            )
        )

    def filetype(self, filename):
        """
        Takes a filename and returns a category based on the file type.
        Categories: word, excel, powerpoint, flash, pdf, image, video, audio, archive, other.
        """
        parts = os.path.splitext(filename)
        if len(parts) < 2:
            return 'other'
        else:
            ext = parts[1][1:].lower()
            if ext == 'png' or ext == 'jpg' or ext == 'jpeg' or ext == 'gif':
                return 'image'
            elif ext == 'avi' or ext == 'mp4' or ext == 'm4v' or ext == 'ogv' or ext == 'wmv' or ext == 'mpg' or ext == 'mpeg':
                return 'video'
            elif ext == 'mp3' or ext == 'm4a' or ext == 'wav' or ext == 'ogg' or ext == 'aiff':
                return 'audio'
            elif ext == 'zip' or ext == '7z' or ext == 'tar' or ext == 'gz' or ext == 'tgz' or ext == 'bz2' or ext == 'rar':
                return 'archive'
            elif ext == 'doc' or ext == 'docx' or ext == 'dot' or ext == 'dotx' or ext == 'rtf':
                return 'word'
            elif ext == 'xls' or ext == 'xlsx' or ext == 'xlt' or ext == 'xltx' or ext == 'csv':
                return 'excel'
            elif ext == 'ppt' or ext == 'pptx':
                return 'powerpoint'
            elif ext == 'flv' or ext == 'swf':
                return 'flash'
            elif ext == 'pdf':
                return 'pdf'
            else:
                return 'other'
