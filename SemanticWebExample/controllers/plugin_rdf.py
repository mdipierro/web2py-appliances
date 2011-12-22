#!/bin/python
# -*- coding: utf-8 -*-
from gluon.storage import Storage
import copy
from string import Template

class Rdf(object):

    def __init__(self, environment, db):
        self.environment = Storage(environment)
        self.auth = environment.get('auth',None) ### mind unused so far
        self.db = db

    def url(self, f=None, args=[], vars={}):
        return str(self.environment.URL(f,args=args, vars=vars))

    def __call__(self):
        args = self.environment.request.args        
        if len(args) < 1:
            redirect(self.url(args='tables'))
        elif args[0] == 'tables':
            return self.tables()
        elif args[0] == 'select':
            return self.select(args(1))
        elif args[0] == 'read':
            return self.read(args(1), args(2))
        else:
            raise HTTP(404)

    def tables(self):
        request = self.environment.request
        descriptionNode = [ { '_rdf:about':self.url(args='tables'),
                              'name':'rdf:Description',
                              'children': [ { 'name': 'rdf:type',
                                              '_rdf:resource': 'http://www.dbs.cs.uni-duesseldorf.de/RDF/relational.owl#Database' } ] } ]
        for table in self.db.tables:
            if hasattr( self.db[table], 'rdf' ):
                descriptionNode[0]['children'].append( { 'name': 'relational:hasTable', \
                                                         '_rdf:resource': self.url( args = [ 'select', str(table) ] ) } )
                                                      
        return self.serialize(namespaces=db.rdf_namespaces, nodes=descriptionNode)

    def read(self, table, record):
        if not (isinstance(table,self.db.Table) or table in self.db.tables) \
                or (isinstance(record, str) and not str(record).isdigit()) \
                or not (hasattr(self.db[table],"rdf")):
            raise HTTP(404)
        if not isinstance(table,self.db.Table):
            table = self.db[table]
        if not "namespaces" in table.rdf:
            raise HTTP(404)

        namespaces = table.rdf['namespaces']

        for namespace in db.rdf_namespaces:
            namespaces[namespace] = db.rdf_namespaces[namespace]

        descriptionNode = { '_rdf:about': self.url( args= [ 'select', str(table), str(record) ] ),
                            'name':'rdf:Description', 'children': [ { 'name': 'rdf_type',
                                                                      '_rdf_resource': table.rdf['type'] } ] }

        rows = db(table.id==record).select()

        for column in rows.colnames:
            if hasattr( table[ column.split('.')[1] ], "rdf" ):
                descriptionNode['children'].append( \
                    self.generate_property( table[ column.split('.')[1] ].rdf, \
                                            rows[0][column.split('.')[1] ] ) )

        rdf_tables = [ rdf_table for rdf_table in self.db.tables \
                           if hasattr(self.db[rdf_table],"rdf") ]

        linked_tables = [ ]
        for rdf_table in rdf_tables:
            for column in self.db[rdf_table].fields:
                if self.db[rdf_table][column].type == ''.join(['reference ',str(table)]):
                    linked_tables.append([ rdf_table, column ])
                    break
            for column in table.fields:
                if( table[column].type == ''.join( [ 'reference ', str(rdf_table) ] ) ):
                    linked_tables.append([ rdf_table, 'id' ])
                    break
        
        for [linked_table,column] in linked_tables:
            rows = db(self.db[linked_table][column]==record).select()
            for row in rows:
                objectProperty = 'relational:references'
                if "references" in table.rdf and linked_table in table.rdf['references']:
                    objectProperty = table.rdf['references'][linked_table]
                descriptionNode['children'].append( { 'name': objectProperty,
                                                      '_rdf_resource': self.url( args = ['read', linked_table, row.id ] ) } )


        mapping_tables = [ mapping_table for mapping_table in self.db.tables \
                               if hasattr(self.db[mapping_table],"rdf_mapping") ]
        mapped_tables = [ ]
        for mapping_table in mapping_tables:
            for column in self.db[mapping_table].fields:
                if self.db[mapping_table][column].type == ''.join(['reference ',str(table)]):
                    for foreign_column in self.db[mapping_table].fields:
                        if self.db[mapping_table][foreign_column].type.find('reference')>=0 and \
                                self.db[mapping_table][foreign_column].type != \
                                ''.join(['reference ',str(table)]) :
                            foreign_table = self.db[mapping_table][foreign_column].type.partition(' ')[2]
                            mapped_tables.append( [ mapping_table, foreign_table, column, foreign_column, 
                                                    self.db[mapping_table]['rdf_mapping'] ] )
                            break
                    break

        for [mapping_table,foreign_table,column,foreign_column,attribute_mapping] in mapped_tables:
            rows=db(self.db[mapping_table][column]==record).select()
            for row in rows:
                objectProperty = 'relational:references'
                if str(table) in db[mapping_table].rdf_mapping and 'reference' in db[mapping_table].rdf_mapping[str(table)]:
                    objectProperty = db[mapping_table].rdf_mapping[str(table)]['reference']
                newNode =  { 'name': objectProperty, 'children': [],
                             '_rdf:resource': self.url( args = [ 'read', foreign_table, row.id ] ) }
                if str(table) in db[mapping_table].rdf_mapping and 'columns' in db[mapping_table].rdf_mapping[str(table)]:
                    for k,v in db[mapping_table].rdf_mapping[str(table)]['columns'].iteritems():
                        newNode['children'].append( { 'name': v, 'value': row[k] } )
                descriptionNode['children'].append(newNode)

        return self.serialize( namespaces=namespaces, nodes=[descriptionNode] )
    
    def select(self, table ):
        request = self.environment.request
        if not isinstance(table,self.db.Table) and not table in self.db.tables:
            raise HTTP(404)
        if not isinstance(table,self.db.Table):
            table = self.db[table]
        if not hasattr(table,'rdf') or not 'namespaces' in table.rdf:
            raise HTTP(404)

        descriptionNode = { '_rdf:about': ''.join( [ self.url(args='select'), '/', str(table) ] ),
                            'name':'rdf:Description',
                            'children': [ { 'name': 'rdf:type',
                                            '_rdf:resource': 'http://www.dbs.cs.uni-duesseldorf.de/RDF/relational.owl#Table' } ] }

        rows = self.db().select(table.ALL)
        for row in rows:
            descriptionNode['children'].append( { 'name': 'relational:has',
                                                  '_rdf_resource': self.url( args = [ 'read', str(table), row.id ] ) } )

        return self.serialize(namespaces=db.rdf_namespaces, nodes=[descriptionNode])


    def serialize(self,**data):
        self.environment.response.headers['Content-Type']='text/xml'
        components=[self.serialize_rec(node) for node in data['nodes']]
        return TAG['rdf:RDF'](*components,**(data['namespaces'])).xml()

    def serialize_rec(self,node):
        if node.has_key('value'):
            components = [node['value']]
        elif node.has_key('children'):
            components = [self.serialize_rec(child) for child in node['children']]
        else:
            components = []
        return TAG[node['name']](*components,**node)

    def generate_property(self,name,value):
        if isinstance(name, str):
            return( { 'name': name,
                      'value': value } )
        elif type(name)==type(dict()):
            node = { }
            for k, v in name.iteritems():
                node[k] = v
                if(k=='children'):
                    node['children'] = self.parse_children(node['children'],value)
                else:
                   d = dict(VALUE=value)
                   k = Template(k).substitute(d)
                   v = Template(v).substitute(d)
                   node[k] = v
        return node

    def parse_children(self,children,value):
        for child in children:
            for k,v in child.iteritems():
                if(k=='children'):
                    v = self.parse_children(v,value)
                else:
                   d = dict(VALUE=value)
                   k = Template(k).substitute(d)
                   v = Template(v).substitute(d)
                   child[k] = v
        return children

def index():
    rows = [A('exposed tables',_href=URL('ld',args='tables'))]
    for table in db.tables:
        if hasattr(db[table],'rdf'):
            rows.append(A('select %s' % table, _href=URL('ld',args=['select',table])))
    return HTML(BODY(TABLE(*rows)))

def ld():
    return '<?xml version="1.0"?>\n'+Rdf(globals(),db)()
