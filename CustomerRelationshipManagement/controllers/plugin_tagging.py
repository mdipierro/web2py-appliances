import re

db_tag = db.plugin_tagging_tag
db_link = db.plugin_tagging_tag_link

def tag():
    table_name=request.args(0)
    record_id=request.args(1)
    if not (auth.user and table_name in db.tables and record_id):
        raise HTTP(404)
    form = SQLFORM.factory(Field('tag_name'))
    if request.vars.tag_name:
        for item in request.vars.tag_name.split(','):
            tag_name = re.compile('\s+').sub(' ',item).strip()
            tag = db(db_tag.name==tag_name).select().first()
            if not tag:
                tag = db_tag.insert(name=tag_name, counter=1)
            link = db(db_link.tag==tag.id)\
                (db_link.table_name==table_name)\
                (db_link.record_id==record_id).select().first()
            if not link:
                db_link.insert(tag=tag.id,
                               table_name=table_name,record_id=record_id)
                tag.update_record(counter=tag.counter+1)
    for key in request.vars:
        if key[:6]=='delete':
            link_id=key[6:]
            link=db_link[link_id]
            del db_link[link_id]
            db_tag[link.tag] = dict(counter=db_tag[link.tag].counter-1)
    links = db(db_link.table_name==table_name)\
              (db_link.record_id==record_id).select()\
              .sort(lambda row: row.tag.name.upper())
    return dict(links=links, form=form)

def tag_cloud():
    tags = db(db_tag.counter>0).select()
    if tags:
        mc = max([tag.counter for tag in tags])
    return DIV(_class='plugin_tagging_tag_cloud',
               *[SPAN(tag.name+' ',_style='font-size:%sem' \
                          % (0.8+1.0*tag.counter/mc)) for tag in tags])

