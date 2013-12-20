class HierarchicalSelect(object):
    def __init__(self, db, table_name, title_field, order_field):
        self.options=[]
        self.db = db
        self.tablename = table_name
        self.fieldname = None
        self.title = title_field
        self.order = order_field
        self.type = None
        self.rows=None
        self.hierarchyseparator = XML("&nbsp;"*4)

    def _childs_list(self, field, depth):
        path = self.hierarchyseparator*depth
       
        path += self.hierarchyseparator
        self.options.append((field['id'], path+field[self.title]))
        [self._childs_list(child, (depth+1)) for child in self.rows.find(lambda row: row.parent == field.id)]   

    def widget(self, field, value):
        self.fieldname = field.name
        self.type = field.type
        self.rows = self.db(self.tablename).select(orderby=self.order)
        self.options.append(("", T('<Empty>'))) #add root node

        [self._childs_list(field,0) for field in self.rows.find(lambda row: row.parent < 1)] 
        opt=[OPTION(name, _value=key) for key,name in self.options]
        sel = SELECT(opt,_id="%s_%s" % (self.tablename, self.fieldname),
                        _class=self.type, 
                        _name=self.fieldname,
                        value=value,
                        requires=self.tablename.parent.requires)
        return sel