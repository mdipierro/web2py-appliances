# -*- coding: utf-8 -*-
from content_plugin import ContentPlugin
from gluon import URL, XML, CAT, I


class ContentPhotoset(ContentPlugin):
    """
    Photo set item
    """

    def create_item_url(self):
        return (
            URL('plugin_photoset', 'create.html'),
            CAT(I(_class="fa fa-object-group"), ' ', self.T('Photo Set'))
        )

    def get_item_url(self, item):
        return URL('plugin_photoset', 'index.html', args=[item.unique_id])

    def get_changelog_url(self, item):
        return URL('plugin_photoset', 'changelog', args=[item.unique_id])

    def get_full_text(self, item):
        """Return full text document, mean for plugins"""
        photoset_content = self.db.plugin_photoset_content(
            item_id=item.unique_id)
        output = self.response.render(
            'plugin_photoset/full_text.txt',
            dict(photoset_content=photoset_content, item=item))
        return unicode(output.decode('utf-8'))

    def preview(self, item):
        super(ContentPhotoset, self).preview(item)
        photoset_content = self.db.plugin_photoset_content(
            item_id=item.unique_id
        )
        return XML(
            self.response.render(
                'plugin_photoset/preview.html',
                dict(item=item, photoset_content=photoset_content))
        )
