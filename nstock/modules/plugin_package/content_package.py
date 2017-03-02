# -*- coding: utf-8 -*-
from content_plugin import ContentPlugin
from gluon import URL, CAT, I, XML


class ContentPackage(ContentPlugin):
    """docstring for ContentPackage."""

    def get_item_url(self, item):
        return URL('plugin_package', 'index.html', args=[item.unique_id])

    def preview(self, item):
        super(ContentPackage, self).preview(item)
        content = self.db.plugin_package_content(item_id=item.unique_id)
        return XML(
            self.response.render(
                'plugin_package/preview.html',
                dict(item=item, p_content=content))
        )

    def create_item_url(self):
        return (
            URL('plugin_package', 'create.html'),
            CAT(I(_class='fa fa-file-archive-o'), ' ', self.T('Package')))

    def get_full_text(self, item):
        """Return full text document, mean for plugins"""
        content = self.db.plugin_package_content(item_id=item.unique_id)
        output = self.response.render(
            'plugin_package/full_text.txt',
            dict(item=item, content=content))
        return unicode(output.decode('utf-8'))

    def get_changelog_url(self, item):
        return URL('plugin_package', 'changelog', args=[item.unique_id])

    def shareItem(self, item_id, src_desk, dst_desk):
        """Share package to user"""
        super(ContentPackage, self).shareItem(item_id, src_desk, dst_desk)
        # on packages, we share each item on the package, and then
        # the package it self
        pkg_item = self.app.getItemByUUID(item_id)
        pkg_content = self.db.plugin_package_content(
            item_id=pkg_item.unique_id)
        for c_item in pkg_content.item_list:
            p_c_item = self.app.getItemByUUID(c_item)
            src = self.db.desk(src_desk)
            if p_c_item.id in src.item_list:
                ct = self.app.getContentType(p_c_item.item_type)
                ct.shareItem(c_item, src_desk, dst_desk)
