for _f in ['plugin_jqgrid/ui.jqgrid.css',
           'plugin_jqgrid/ui-darkness/jquery-ui-1.8.1.custom.css',
           'plugin_jqgrid/jquery-ui-1.7.2.custom.min.js',
           'plugin_jqgrid/i18n/grid.locale-en.js',              
           'plugin_jqgrid/jquery.jqGrid.min.js']:
    response.files.append(URL(r=request,c='static',f=_f))

def plugin_jqgrid(table,fieldname=None,fieldvalue=None,col_widths={},
                  _id=None,columns=None,col_width=80,width=700,height=300):
    """
    just do to embed the jqGrid with ajax search capability and pagination
    {{=plugin_jqgrid(db.tablename)}}
    - table is the db.tablename
    - fieldname, fieldvalue are an optional filter (fieldname==fieldvalue)
    - _id is the "id" of the DIV that contains the jqGrid
    - columns is a list of columns names to be displayed
    - cold_width is the width of each column
    - height is the height of the jqGrid
    """
    from gluon.serializers import json
    _id = 'jqgrid_%s' % table
    columns = columns or [x for x in table.fields if table[x].readable]
    colnames = [x.replace('_',' ').capitalize() for x in columns]
    colmodel = [{'name':x,'index':x, 'width':col_widths.get(x,col_width), 'sortable':True} \
                    for x in columns if table[x].readable]    
    callback = URL(r=request,c='plugin_jqgrid',f='data',
                   vars=dict(tablename=table._tablename,
                             columns=','.join(columns),
                             fieldname=fieldname or '',
                             fieldvalue=fieldvalue,
                             ))
    script="""
jQuery(document).ready(function(){jQuery("#%(id)s").jqGrid({ url:'%(callback)s', datatype: "json", colNames: %(colnames)s,colModel:%(colmodel)s, rowNum:10, rowList:[20,50,100], pager: '#%(id)s_pager', viewrecords: true,height:%(height)s});jQuery("#%(id)s").jqGrid('navGrid','#%(id)s_pager',{search:true,add:false,edit:false,del:false});jQuery("#%(id)s").setGridWidth(%(width)s,false);});
""" % dict(callback=callback,colnames=json(colnames),
           colmodel=json(colmodel),id=_id,height=height,width=width)
    return TAG[''](TABLE(_id=_id),
                   DIV(_id=_id+"_pager"),
                   SCRIPT(script))
