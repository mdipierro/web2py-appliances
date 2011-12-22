# coding: utf8
# try something like
orcadb=DAL("sqlite://orca.db")

current_user_alias = (auth.user and auth.user.first_name+" "+auth.user.last_name) or "Anónimo"

orcadb.define_table("type_graph",
      SQLField("name", notnull=True, default=None),
      SQLField("description", "text", default=None),
      SQLField("filter", notnull=True, default=None)) 
     
orcadb.define_table("grupo",
      SQLField("name", notnull=True, default=None))
      
orcadb.define_table("grupo_graph",
      SQLField("name", default=current_user_alias),
      SQLField("id_type_graph", orcadb.type_graph),
      SQLField("id_grupo", orcadb.grupo))


   
"""
Relations between tables (remove fields you don't need from requires)
"""
orcadb.grupo_graph.id_type_graph.requires=IS_IN_DB(orcadb,'type_graph.id', 'type_graph.name')
orcadb.grupo_graph.id_grupo.requires=IS_IN_DB(orcadb,'grupo.id', 'grupo.name')
