# -*- coding: utf-8 -*-
from content_plugin import ContentPlugin
from gluon import URL, XML, CAT, I


class ContentText(ContentPlugin):

    def create_item_url(self):
        return (
            URL('plugin_text', 'create.html'),
            CAT(I(_class="fa fa-file-text-o"), ' ', self.T('Text')))

    def get_item_url(self, item):
        return URL('plugin_text', 'index.html', args=[item.unique_id])

    def get_changelog_url(self, item):
        return URL('plugin_text', 'changelog', args=[item.unique_id])

    def get_full_text(self, item):
        """Return full text document, mean for plugins"""
        text_content = self.db.plugin_text_text(item_id=item.unique_id)
        output = self.response.render(
            'plugin_text/full_text.txt',
            dict(text_content=text_content, item=item))
        return unicode(output.decode('utf-8'))

    def preview(self, item):
        super(ContentText, self).preview(item)
        content = self.db.plugin_text_text(item_id=item.unique_id)
        return XML(self.response.render(
            'plugin_text/preview.html',
            dict(item=item, p_content=content)))
