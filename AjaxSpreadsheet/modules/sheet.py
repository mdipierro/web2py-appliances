"""
Developed by Massimo Di Pierro, optional component of web2py, GPL2 license.
"""
import re
import pickle
import copy

def quote(text):
    return str(text).replace('\\','\\\\').replace("'","\\'")

class Node:
    """
    Example::

         # controller
         from gluon.contrib.spreadsheet import Sheet
         def index():
             if request.args:
             sheet = Sheet.loads(session.psheet)
             jquery=sheet.process(request)
             session.psheet=sheet.dumps()
             return jquery
         else:
             sheet=Sheet(10,10,URL(r=request))
             #sheet = Sheet.loads(session.psheet)
             sheet.cell('r0c3',value='=r0c0+r0c1+r0c2',readonly=True)        
             session.psheet = sheet.dumps()
             return dict(sheet=sheet)

         # view
         {{extend 'layout.html'}}
         <form>
          <table spacing="0" border="0" padding="0">
           {{for r in xrange(sheet.rows):}}
            <tr>
             {{for c in xrange(sheet.cols):}}
             <td>
              {{=XML(sheet.nodes['r%sc%s'%(r,c)].xml())}}
             </td>
             {{pass}}
            </tr>
           {{pass}}
          </table>
         </form>
    """
    def __init__(self,name,value,url='.',readonly=False,active=True,onchange=None):
        self.url=url
        self.name=name
        self.value=value
        self.computed_value=''
        self.incoming={}
        self.outcoming={}
        self.readonly=readonly
        self.active=active
        self.onchange=onchange
        self.size=6
        self.locked=False

    def xml(self):
        return """<input name="%s" id="%s" value="%s" size="%s" 
        onkeyup="ajax('%s/keyup',['%s'],':eval');"
        onfocus="ajax('%s/focus',['%s'],':eval');"
        onblur="ajax('%s/blur',['%s'],':eval');" %s/>
        """ % (self.name,self.name,self.computed_value,self.size,
               self.url,self.name,self.url,self.name,self.url,self.name,
               (self.readonly and 'readonly ') or '')
    def __repr__(self):
        return '%s:%s' % (self.name,self.computed_value)

class Sheet:

    regex=re.compile('(?<!\w)[a-zA-Z_]\w*')    

    re_strings = re.compile(r'(?P<name>'
                            + r"[uU]?[rR]?'''([^']+|'{1,2}(?!'))*'''|"
                            + r"'([^'\\]|\\.)*'|"
                            + r'"""([^"]|"{1,2}(?!"))*"""|'
                            + r'"([^"\\]|\\.)*")', re.DOTALL)    

    def dumps(self):
        dump=pickle.dumps(self)
        return dump

    @staticmethod
    def loads(data):
        sheet=pickle.loads(data)
        return sheet

    def process(self,request):
        """
        call this in action that creates table, it will handle ajax callbacks
        """
        cell=request.vars.keys()[0]
        if request.args(0)=='focus':
            return "jQuery('#%s').val('%s');" % (cell,quote(self[cell].value))
        value = request.vars[cell]
        self[cell]=value
        if request.args(0)=='blur':
            return "jQuery('#%s').val('%s');" % (cell,quote(self[cell].computed_value))
        elif request.args(0)=='keyup':
            jquery=''
            for other_key in self.modified:
                if other_key!=cell:
                    jquery+="jQuery('#%s').val('%s');" % \
                        (other_key,quote(self[other_key].computed_value))
        return jquery

    def __init__(self,rows,cols,url='.'):
        self.rows=rows
        self.cols=cols
        self.url=url
        self.nodes={}
        self.error='ERROR: %(error)s'
        self.allowed_keywords=['for','in','if','else','and','or','not',
                               'i','j','k','x','y','z','sum']
        self.environment={}
        [self.cell('r%sc%s'%(k/cols,k%cols),'0.0') for k in xrange(rows*cols)]
        exec('from math import *',{},self.environment)

    def delete_from(self,other_list):
        indices = [k for (k,node) in enumerate(other_list) if k==node] 
        if indices: del other_list[indices[0]]

    def changed(self,node,changed_nodes=[]):
        for other_node in node.outcoming:
            if not other_node in changed_nodes:
                changed_nodes.append(other_node)
                self.changed(other_node,changed_nodes)
        return changed_nodes

    def define(self,name,obj):
        self.environment[name]=obj

    def cell(self,key,value,readonly=False,active=True,onchange=None):
        """
        key is the name of the cell
        value is the initial value of the cell. It can be a formula "=1+3"
        a cell is active if it evaluates formuls        
        """
        if not self.regex.match(key): raise SyntaxError, "Invalid cell name"
        node=Node(key,value,self.url,readonly,active,onchange)
        self.nodes[key]=node
        self[key]=value
        

    def __setitem__(self,key,value):
        node=self.nodes[key]
        node.value=value
        if value[:1]=='=' and node.active:
            # clear all edges involving current node
            for other_node in node.incoming:
                del other_node.outcoming[node]
            node.incoming.clear()
            # build new edges
            command = self.re_strings.sub("''",value[1:])
            node.locked=False
            for match in self.regex.finditer(command):
                other_key=match.group()
                if other_key==key:
                    self.computed_value=self.error % dict(error='cycle')
                    self.modified={}
                    break
                if other_key in self.nodes:
                    other_node=self.nodes[other_key]           
                    other_node.outcoming[node]=True
                    node.incoming[other_node]=True                    
                elif not other_key in self.allowed_keywords and \
                        not other_key in self.environment:
                    node.locked=True
                    node.computed_value=self.error % dict(error='invalid keyword: '+other_key)
                    self.modified={}
                    break                
            self.compute(node)
        else:
            try:
                node.computed_value=int(node.value)                
            except:
                try:
                    node.computed_value=float(node.value)
                except:
                    node.computed_value=node.value
            self.environment[key]=node.computed_value
            if node.onchange: node.onchange()
        self.modified=self.iterate(node)

    def compute(self,node):
        if node.value[:1]=='=' and not node.locked:
            try:
                exec('__value__='+node.value[1:],{},self.environment)
                node.computed_value=self.environment['__value__']
                del self.environment['__value__']            
            except Exception,e:
                node.computed_value=self.error % dict(error=str(e))
        self.environment[node.name]=node.computed_value
        if node.onchange: node.onchange()

    def iterate(self,node):
        output={node.name:node.computed_value}
        changed_nodes = self.changed(node)
        while changed_nodes:
            ok=False          
            set_changed_nodes=set(changed_nodes)
            for (k,other_node) in enumerate(changed_nodes):
                #print other_node, changed_nodes
                if not set(other_node.incoming.keys()).intersection(set_changed_nodes):
                    #print 'ok'
                    self.compute(other_node)
                    output[other_node.name]=other_node.computed_value
                    #print other_node
                    del changed_nodes[k]
                    ok=True
                    break
            if not ok: return {}
        return output

    def __getitem__(self,key):
        return self.nodes[key]
            
if __name__=='__main__':
    s=Sheet(0,0)
    s.cell('a',value="2")
    s.cell('b',value="=sin(a)")
    s.cell('c',value="=cos(a)**2+b*b")
    print s['c'].computed_value
