from gluon.html import URL

class HierarchicalMenu(object):
    def __init__(self):
        self.menu = None
        self.rows = None
    
    def _childs_list(self, record):
        myChild = [self._childs_list(child) for child in self.rows.find(lambda row: row.parent == record.id)]
        return [record.title, False,URL('pages','show_page', args=record.url),myChild]   

    def create_menu(self, rows):
        self.rows = rows
        self.menu = [self._childs_list(field) for field in self.rows.find(lambda row: row.parent < 1)] 
        return self.menu