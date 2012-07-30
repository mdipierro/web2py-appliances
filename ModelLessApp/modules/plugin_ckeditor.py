# -*- coding: utf-8 -*-

###############################################################################
# Movuca - The Social CMS
# Copyright (C) 2012  Bruno Cezar Rocha <rochacbruno@gmail.com>

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.

# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
#
# This file is based on work of Ross Peoples
#
###############################################################################


import os
from gluon import *
from gluon.storage import Storage


class CKEditor(object):
    """
    Integrates CKEditor nicely into web2py.
    """
    def __init__(self, db=None, theme_name='basic'):
        """
        Initializes the CKEditor module. Requires a DAL instance.
        """
        #self.db = db
        self.settings = Storage()
        self.settings.table_upload = None
        self.settings.table_upload_name = 'plugin_ckeditor_upload'
        self.settings.extra_fields = {}
        self.settings.url_upload = URL('plugin_ckeditor', 'upload')
        self.settings.url_browse = URL('plugin_ckeditor', 'browse')
        self.settings.browse_filter = {}
        self.settings.file_length_max = 10485760    # 10 MB
        self.settings.file_length_min = 0           # no minimum
        self.settings.spellcheck_while_typing = False
        self.T = current.T
        self.theme_name = theme_name

        #current.plugin_ckeditor = self

        #self.define_tables()

    def define_tables(self, migrate=True, fake_migrate=False):
        """
        Called after settings are set to create the required tables for dealing
        with file uploads from CKEditor.
        """

        from myapp import MyApp
        app = MyApp()
        auth = app.auth
        from datamodel.post import Post as PostModel
        self.db = app.db([PostModel])

        upload_name = self.settings.table_upload_name

        self.settings.table_upload = self.db.define_table(upload_name,
            Field('title', length=255),
            Field('filename', length=255),
            Field('flength', 'integer'),
            Field('mime_type', length=128),
            Field('upload', 'upload'),
            Field('user_id', 'integer', default=app.session.auth.user.id if app.session.auth else 0),
            Field("created_on", "datetime", default=app.request.now),
            *self.settings.extra_fields.get(upload_name, []),
            **dict(migrate=migrate,
            fake_migrate=fake_migrate,
            format='%(title)s')
        )
        self.settings.table_upload.upload.requires = [
            IS_NOT_EMPTY(),
            IS_LENGTH(maxsize=self.settings.file_length_max, minsize=self.settings.file_length_min),
        ]

    def edit_in_place(self, selector, url):
        """
        Creates an instance of CKEditor that will edit selected HTML elements
        in place and provide AJAX saving capabilities. To start editing, the
        user will need to double click on one of the matched selectors.

        Requires a URL to return saved data to. The data will be stored in
        request.vars.content.

        NOTE: This should not be used for multi-tenant applications or where
        there is a possibility a malicious user could tamper with the variables.
        """
        javascript = self.load()

        return XML(
            """
            %(javascript)s
            <script type="text/javascript">
                jQuery(function() {
                    jQuery('%(selector)s').ckeip({
                        e_url: '%(url)s',
                        data: {'object': jQuery('%(selector)s').attr('data-object'),
                               'id': jQuery('%(selector)s').attr('data-id')},
                        ckeditor_config: ckeditor_config(),
                    });
                });
            </script>
            """ % dict(
                javascript=javascript,
                selector=selector,
                url=url,
            )
        )

    def bulk_edit_in_place(self, selectorlist, url):
        """
        Creates an instance of CKEditor that will edit selected HTML elements
        in place and provide AJAX saving capabilities. To start editing, the
        user will need to double click on one of the matched selectors.

        Requires a URL to return saved data to. The data will be stored in
        request.vars.content.

        NOTE: This should not be used for multi-tenant applications or where
        there is a possibility a malicious user could tamper with the variables.
        """
        basic = self.load(toolbar='basic')
        javascript = [XML("""
        <script type="text/javascript">
        function removecomment(selector) {
            if (confirm("%s")) {
                ajax('%s/'+selector,[1],'');
                jQuery('#'+selector).parent().hide();
                return false;
                }
        }
        </script>
        """ % (self.T("Are you sure you want to delete this comment?"),
               URL('article', 'removecomment'))
               )
        ]

        [javascript.append(XML(
            """
            <script type="text/javascript">
                jQuery(function() {
                    jQuery('#%(selector)s').ckeip({
                        e_url: '%(url)s',
                        data: {'object': jQuery('#%(selector)s').attr('data-object'),
                               'id': jQuery('#%(selector)s').attr('data-id')},
                        ckeditor_config: ckeditor_config(),
                    });
                    jQuery("[ <em class='double_message'> %(double_message)s</em> | <a href='#removecomment' onclick=removecomment('%(selector)s') >%(delete_message)s</a> ]").appendTo(jQuery('#%(selector)s').parent());
                });
            </script>
            """ % dict(
                selector=selector,
                url=url,
                double_message=self.T("Double click the text above to edit"),
                delete_message=self.T("Delete this comment")
            )
        )) for selector in selectorlist]

        return (basic, CAT(*javascript))

    def widget(self, field, value):
        """
        To be used with db.table.field.widget to set CKEditor as the desired widget for the field.
        Simply set db.table.field.widget = ckeditor.widget to use the CKEditor widget.
        """
        self.define_tables()
        javascript = self.load('.plugin_ckeditor')

        return CAT(
            TEXTAREA(
                value if value not in ['None', None] else '',
                _id=str(field).replace('.', '_'),
                _name=field.name,
                _class='text plugin_ckeditor',
                #_value=value,
                _cols=80,
                _rows=10,
            ),
            javascript
        )

    def basicwidget(self, field, value):
        """
        To be used with db.table.field.widget to set CKEditor as the desired widget for the field.
        Simply set db.table.field.widget = ckeditor.widget to use the CKEditor widget.
        """
        self.define_tables()
        javascript = self.load('.plugin_ckeditor', toolbar='basic')

        return CAT(
            TEXTAREA(
                value if value not in ['None', None] else '',
                _id=str(field).replace('.', '_'),
                _name=field.name,
                _class='text plugin_ckeditor',
                #_value=value,
                _cols=80,
                _rows=10,
            ),
            javascript
        )

    def handle_upload(self):
        """
        Gets an upload from CKEditor and returns the new filename that can then be
        inserted into a database. Returns (new_filename, old_filename, length, mime_type)
        """
        upload = current.request.vars.upload
        path = os.path.join(current.request.folder, 'uploads')
        if upload != None:
            if hasattr(upload, 'file'):
                form = SQLFORM.factory(
                    Field('upload', 'upload', requires=IS_NOT_EMPTY(), uploadfolder=path),
                    table_name=self.settings.table_upload_name
                )

                old_filename = upload.filename
                new_filename = form.table.upload.store(upload.file, upload.filename)
                length = os.path.getsize(os.path.join(path, new_filename))
                mime_type = upload.headers['content-type']

                return (new_filename, old_filename, length, mime_type)
            else:
                raise HTTP(401, 'Upload is not proper type.')
        else:
            raise HTTP(401, 'Missing required upload.')

    def load(self, selector=None, toolbar='full'):
        """
        Generates the required JavaScript for CKEditor. If selector is set,
        then immediately turns the selected HTML element(s) into CKEditor
        instances. Otherwise, a manual JavaScript call to plugin_ckeditor_init()
        is required with the desired selector.
        """
        #if self.settings.loaded:
        #    return ''
        #else:
        #    self.settings.loaded = True

        tools = {
            'full': """[
                        { name: 'document', items : [ 'Source','-','DocProps','Preview','Print','-','Templates' ] },
                        { name: 'clipboard', items : [ 'Cut','Copy','Paste','PasteText','PasteFromWord','-','Undo','Redo' ] },
                        { name: 'editing', items : [ 'Find','Replace','-','SpellChecker', 'Scayt' ] },
                        { name: 'basicstyles', items : [ 'Bold','Italic','Underline','Strike','Subscript','Superscript','-','RemoveFormat' ] },
                        { name: 'paragraph', items : [ 'NumberedList','BulletedList','-','Outdent','Indent','-','Blockquote','CreateDiv','-','JustifyLeft','JustifyCenter','JustifyRight','JustifyBlock' ] },
                        { name: 'links', items : [ 'Link','Unlink','Anchor' ] },
                        { name: 'insert', items : [ 'Image','Table','HorizontalRule','Smiley','SpecialChar','PageBreak','Iframe' ] },
                        { name: 'styles', items : [ 'Styles','Format','Font','FontSize' ] },
                        { name: 'colors', items : [ 'TextColor','BGColor' ] },
                        { name: 'tools', items : [ 'Maximize', 'ShowBlocks','-','About','syntaxhighlight' ] }
                     ]""",
            'basic': """[
                        { name: 'basicstyles', items : [ 'Bold','Italic','Underline','Strike','Subscript','Superscript','-','RemoveFormat' ] },
                        { name: 'paragraph', items : [ 'NumberedList','BulletedList','-','-','Blockquote','-','JustifyLeft','JustifyCenter','JustifyRight','JustifyBlock' ] },
                        { name: 'links', items : [ 'Link','Unlink','Anchor' ] },
                        { name: 'insert', items : [ 'Image','Table','Smiley','SpecialChar'] },
                        { name: 'colors', items : [ 'TextColor','syntaxhighlight'] },
                     ]""",
        }

        upload_url = self.settings.url_upload
        browse_url = self.settings.url_browse
        ckeditor_js = URL('static', 'plugin_ckeditor/ckeditor.js')
        jquery_js = URL('static', 'plugin_ckeditor/adapters/jquery.js')
        ckeip_js = URL('static', 'plugin_ckeditor/ckeip.js')
        contents_css = "['%s', '%s']" % (URL('static', '%s/css/web2py.css' % self.theme_name), URL('static', 'plugin_ckeditor/contents.css'))

        immediate = ''
        if selector:
            immediate = """
                jQuery(function() {
                    var config = ckeditor_config();
                    jQuery('%s').ckeditor(config);
                });
            """ % selector

        scayt = 'false'
        if self.settings.spellcheck_while_typing:
            scayt = 'true'

        return XML(
            """
            <style type="text/css">
                .cke_skin_kama input.cke_dialog_ui_input_text, .cke_skin_kama input.cke_dialog_ui_input_password {
                    margin: 0;
                }

                .ckeip_toolbar {
                    position: relative;
                    background: white;
                    border-top: 1px solid #D3D3D3;
                    border-left: 1px solid #D3D3D3;
                    border-right: 1px solid #D3D3D3;
                    -moz-border-radius-topleft: 5px;
                    -moz-border-radius-topright: 5px;
                    border-top-left-radius: 5px;
                    border-top-right-radius: 5px;
                    padding: 0.5em;
                    margin-bottom: -5px;
                    z-index: 1;
                }
            </style>
            <script type="text/javascript" src="%(ckeditor_js)s"></script>
            <script type="text/javascript" src="%(jquery_js)s"></script>
            <script type="text/javascript" src="%(ckeip_js)s"></script>
            <script type="text/javascript">
                function ckeditor_config() {
                    return {
                        contentsCss: %(contents_css)s,
                        filebrowserUploadUrl: '%(upload_url)s',
                        filebrowserBrowseUrl: '%(browse_url)s',
                        toolbar: %(toolbar)s,
                        scayt_autoStartup: %(scayt)s,
                        uiColor: 'transparent',
                        //extraPlugins: 'syntaxhighlight',
                    }
                }
                %(immediate)s
            </script>
            """ % dict(
                ckeditor_js=ckeditor_js,
                jquery_js=jquery_js,
                ckeip_js=ckeip_js,
                contents_css=contents_css,
                upload_url=upload_url,
                browse_url=browse_url,
                scayt=scayt,
                immediate=immediate,
                toolbar=tools[toolbar],
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



                       # [
                       #      {name: 'clipboard', items: ['Cut', 'Copy', 'Paste', 'PasteText', 'PasteFromWord', '-', 'Undo', 'Redo']},
                       #      {name: 'editing', items: ['Find', 'Replace', '-', 'SelectAll', '-', 'SpellChecker', 'Scayt']},
                       #      {name: 'links', items: ['Link', 'Unlink', 'Anchor']},
                       #      {name: 'insert', items: ['Image', 'Flash', 'Table', 'SpecialChar']},
                       #      {name: 'tools', items: ['Maximize', 'ShowBlocks', '-', 'Source']},
                       #      '/',
                       #      {name: 'styles', items: ['Format', 'Font', 'FontSize']},
                       #      {name: 'basicstyles', items: ['Bold', 'Italic', 'Underline', 'Strike', '-', 'RemoveFormat']},
                       #      {name: 'paragraph', items: ['NumberedList', 'BulletedList', '-', 'Outdent', 'Indent', 'JustifyLeft', 'JustifyCenter', 'JustifyRight', 'JustifyBlock']},
                       #  ]
