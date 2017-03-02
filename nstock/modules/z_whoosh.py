# -*- coding: utf-8 -*-
from whoosh.fields import Schema, TEXT, ID
from whoosh.index import create_in, open_dir
from gluon import current
import os
# from https://github.com/web2py/scaffold
# On new installations remove the 'whoosh' directory from the package
# and don't include it on the repository


class Whoosh(object):

    def __init__(self, user_id=None):
        self.index = os.path.join(current.request.folder, 'whoosh')
        if not os.path.exists(self.index):
            os.makedirs(self.index)
            self.schema = Schema(id=ID(unique=True, stored=True), text=TEXT)
            self.ix = create_in(
                self.index, schema=self.schema)
        else:
            self.ix = open_dir(self.index)

    def add_to_index(self, item_id, text):
        from whoosh.writing import AsyncWriter
        writer = AsyncWriter(self.ix)
        writer.update_document(id=item_id, text=text.lower())
        writer.commit()

    def search(self, text, page=1, pagelen=500):
        from whoosh.qparser import QueryParser
        text = text.lower()
        with self.ix.searcher() as searcher:
            query = QueryParser("text", self.ix.schema).parse(
                unicode(text.decode('utf-8')))
            results = searcher.search_page(query, page, pagelen)
            return [r['id'] for r in results]
