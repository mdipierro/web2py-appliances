# -*- coding: utf-8 -*-
# This plugins is licensed under the MIT license: http://www.opensource.org/licenses/mit-license.php
# Authors: Kenji Hosoda <hosoda@s-cubism.jp>
from gluon import *

def color_widget(field, value, **attributes):
    for _url in (URL('static','plugin_color_widget/css/colorpicker.css'),
                 URL('static','plugin_color_widget/css/layout.css'),
                 URL('static','plugin_color_widget/js/colorpicker.js'),
                 URL('static','plugin_color_widget/js/eye.js'),
                 URL('static','plugin_color_widget/js/utils.js'),
                 URL('static','plugin_color_widget/js/layout.js'),):
        if _url not in current.response.files:
            current.response.files.append(_url)
            
    _id = '%s_%s' % (field._tablename, field.name)
    attr = dict(
            _type = 'text', value = (value!=None and str(value)) or '',
            _id = _id, _name = field.name, requires = field.requires,
            _class = 'string',
            )

    script = SCRIPT("""
$(document).ready(function() {
    var picker = $('#%(id)s');
    picker.ColorPicker({
onSubmit: function(hsb, hex, rgb, el) {
    $(el).val(hex);
    $(el).ColorPickerHide();
    $(el).parent().parent().css('background', '#'+hex);
},
onBeforeShow: function () {
    $(this).ColorPickerSetColor(this.value);
}
})
.bind('keyup', function(){
$(this).ColorPickerSetColor(this.value);
});
picker.each(function() {
if (this.value) {
    $(this).parent().parent().css('background', '#' + this.value);
}
});
});
    """ % dict(id=_id))
    return SPAN(script, INPUT(**attr), **attributes)
